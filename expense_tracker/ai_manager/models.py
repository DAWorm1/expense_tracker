from django.db import models
from .validators import CSV_Validator
from langchain_community.llms import Ollama
import csv
import os

from django.conf import settings

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader


AVAILABLE_MODELS = [
    ('llama2:7b-text', 'llama2:7b-text'),
]

# Create your models here.
class GetVendor_AIModel(models.Model):
    system_message = models.TextField()
    prompt = models.TextField()
    model = models.CharField(max_length=255,
                             choices=AVAILABLE_MODELS,
                             unique=True)
    input_list = models.TextField(validators=[CSV_Validator],blank=True,default="")
    db = models.CharField(max_length=255, blank=True, default="")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} > {self.model}"
    
    def add_item_to_database(self,description,vendor):
        with open("tmp.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Transaction", "Name"])
            writer.writerow([description,vendor])
        
        self.add_csv_to_database("tmp.csv")
        os.remove("tmp.csv")
    
    def add_csv_to_database(self,csv_file, source_column="Transaction"):
        loader = CSVLoader(file_path=csv_file,source_column=source_column)
        data = loader.load()
        print(f"Data: {data}")
        self._add_documents_to_database(data)
    
    def _add_documents_to_database(self, documents: list):
        if not self.db_cache:
            self.db_cache = FAISS.load_local(self.db, HuggingFaceEmbeddings())
        assert self.db != ""


        print(f"Documents: {documents}")
        additions_db = FAISS.from_documents(documents,HuggingFaceEmbeddings())
        self.db_cache.merge_from(additions_db)
        self.db_cache.save_local(self.db)
        print(f"Added {documents} to the database.")
        
    
    async def _get_example(self, input):
        if self.db_cache is None:
            embedder = HuggingFaceEmbeddings()    
            self.db_cache = FAISS.load_local(self.db,embedder)

        docs = await self.db_cache.asimilarity_search(input)
        return docs
    
    def _get_db_object(self):
        return FAISS.load_local(self.db,HuggingFaceEmbeddings)
    
    async def get_vendor_from_description(self, description: str):
        print(f"Getting the vendor for \nTransaction: {description}\n################")
        llm = Ollama(model=self.model)

        # Get example input and output
        example_docs = await self._get_example(description)
        similar_example = example_docs[0].page_content

        prompt = self.prompt.format(input=description, example=similar_example)
        prompt = self.system_message + "\n\n" + prompt

        print(f"##################\nFinal Prompt:\n{prompt}\n######################")

        output:str = await llm.ainvoke(prompt)

        # Parse output
        lines = output.splitlines()

        # Get the first line that isn't empty. If there are two quotations marks, get the content in between them
        # If there is an open parenthesis, set the end point to the open parenthesis. 
        # Otherwise just return the entire line. 
        for line in lines:
            end = None
            start = None
            if line.strip() == "":
                continue
            if "(" in line:
                end = line.find("(")
            if '"' in line and line.count('"') == 2:
                start = line.find('"')
                end = line.find('"',start+1)

            if start is not None and end is not None:
                return line[start:end]
            
            if end is not None:
                return line[:end]
            
            if start is not None:
                return line[start:]
            
            return line
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if not self.pk:
            return
        if self.db == "":
            print("initializing DB for first time")
            loader = CSVLoader(file_path=settings.BASE_DIR / "ai_manager/initial_data.csv",source_column="Transaction")
            data = loader.load()

            print("Creating embeddings from documents")
            db_obj = FAISS.from_documents(data, HuggingFaceEmbeddings())
            self.db_cache = db_obj
            print("Saving")
            db_obj.save_local("vendor_from_descriptions")
            self.db = "vendor_from_descriptions"
            self.save(update_fields=["db",])
        else:
            self.db_cache = FAISS.load_local(self.db, HuggingFaceEmbeddings())

            

from django.core.management.base import BaseCommand, CommandError
from ai_manager.models import GetVendor_AIModel
from account_manager.models import Transaction
import asyncio

class Command(BaseCommand):

    def get_transactions(self,transaction_ids,transactions,model):
        for id in transaction_ids:
            tr = Transaction.objects.get(pk = id)
            if not isinstance(tr, Transaction):
                self.stdout.write(
                    self.style.ERROR(f"Could not get the transaction with ID: {id}")
                )
                continue

            transactions[id] = model.get_vendor_from_description(tr.description)

        print(f"Transactions: {transactions}")
        return transactions

    async def get_llm_result(self, transactions):
        outputs = await asyncio.gather(*[transaction for id,transaction in transactions.items()])
        
        print(f"Outputs: {outputs}")
        return dict(zip(list(transactions.keys()),outputs))
       
    def add_arguments(self, parser):
        parser.add_argument("transaction_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        model = GetVendor_AIModel.objects.all()[0]

        transactions = self.get_transactions(options["transaction_ids"],{},model)
        
        outputs = asyncio.run(self.get_llm_result(transactions))

        for id, vendor in outputs.items():
            Transaction.objects.filter(pk=id).update(vendor=vendor)
            self.stdout.write(
                self.style.SUCCESS(f"Saved Transaction {id} with vendor: {vendor}")
            )
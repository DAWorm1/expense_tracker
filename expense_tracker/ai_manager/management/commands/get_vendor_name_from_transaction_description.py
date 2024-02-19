from django.core.management.base import BaseCommand, CommandError
from ai_manager.models import GetVendor_AIModel
from account_manager.models import Transaction
import asyncio
import logging

class Command(BaseCommand):
    logger = logging.getLogger("AI")

    def get_transaction_coroutines(self,transaction_ids: list[int],transactions: dict,model: GetVendor_AIModel):
        for id in transaction_ids:
            tr = Transaction.objects.get(pk = id)
            if not isinstance(tr, Transaction):
                self.stdout.write(
                    self.style.ERROR(f"Could not get the transaction with ID: {id}")
                )
                self.logger.log(logging.ERROR,f"Could not get the transaction with ID: {id}")
                continue

            transactions[id] = model.get_vendor_from_description(tr.description)

        print(f"Transactions: {transactions}")
        return transactions

    async def get_llm_result(self, tr_coroutines):
        outputs = await asyncio.gather(*[coroutine for id,coroutine in tr_coroutines.items()])
        
        return dict(zip(list(tr_coroutines.keys()),outputs))
       
    def add_arguments(self, parser):
        parser.add_argument("transaction_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        model = GetVendor_AIModel.objects.all()[0]

        tr_coroutines = self.get_transaction_coroutines(options["transaction_ids"],{},model)
        
        outputs = asyncio.run(self.get_llm_result(tr_coroutines))

        for id, vendor in outputs.items():
            Transaction.objects.filter(pk=id).update(vendor=vendor)
            self.logger.log(
                logging.INFO,
                f"Saved Transaction {id} with vendor: {vendor}"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Saved Transaction {id} with vendor: {vendor}")
            )
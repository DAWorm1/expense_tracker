from django.db import models
import pandas as pd
from .templates import TransactionTemplate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=50)

    def _is_duplicate_transaction(self, transaction: TransactionTemplate) -> bool:
        duplicate_suspicion = 0

        # Look for transactions on the same posted day
        same_posted_day_transactions: 'QuerySet[Transaction]' = self.transactions.filter(
            posted_date = transaction.posted_date
        )

        for potential_duplicate in same_posted_day_transactions:
            # Check amount
            if transaction.credit_amount > 0 and potential_duplicate.credit_amount > 0:
                if transaction.credit_amount - potential_duplicate.credit_amount < .05: duplicate_suspicion += 2
            if transaction.debit_amount > 0 and potential_duplicate.debit_amount > 0:
                if transaction.debit_amount - potential_duplicate.debit_amount < .05: duplicate_suspicion += 2

            # Check description
            if transaction.description == potential_duplicate.description: duplicate_suspicion += 3

            # Check category
            if transaction.category == potential_duplicate.category: duplicate_suspicion += 1

        if duplicate_suspicion > 4:
            return True
        else:
            return False
        

    def import_transactions_from_template(self, transactions: list[TransactionTemplate]) -> tuple[bool, list[str]]:
        transactions_imported = 0
        transactions_skipped = 0
        
        # Make sure we haven't already processed the transaction
        for tr in transactions:
            if (self._is_duplicate_transaction(tr)):
                transactions_skipped += 1
                continue

            Transaction.objects.create(
                transaction_date=tr.transaction_date,
                posted_date=tr.posted_date,
                account=self,
                description=tr.description,
                category=tr.category,
                category_certainty=None,
                debit_amount=tr.debit_amount,
                credit_amount=tr.credit_amount
            )
            transactions_imported += 1

        if transactions_imported == 0: return (False,[f"No transactions were imported. {transactions_skipped} transactions were skipped"])

        return (True,[f"{transactions_skipped} transaction(s) were skipped.\n{transactions_imported} transaction(s) were imported to {self}."])
    
    def __str__(self) -> str:
        return f"Account: {self.name}"

class Transaction(models.Model):
    transaction_date = models.DateField(blank=True)
    posted_date = models.DateField(blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    description = models.CharField(max_length=150, default="")
    category = models.TextField(default="", blank=True)
    category_certainty = models.FloatField(blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.00)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.00)
    
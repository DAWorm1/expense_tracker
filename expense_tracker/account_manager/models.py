from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager
import pandas as pd
from .templates import TransactionTemplate
from typing import TYPE_CHECKING, Any
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

if TYPE_CHECKING:
    from django.db.models import QuerySet


# Create your models here.
class Account(models.Model):
    TYPES = (
        (1,"Checking Account"),
        (2,"Credit Card Account")
    )

    name = models.CharField(max_length=50)
    type = models.IntegerField(choices=TYPES,default=1)

    def _is_duplicate_transaction(self, transaction: TransactionTemplate) -> bool:
        duplicate_suspicion = 0

        # Look for transactions on the same posted day
        same_posted_day_transactions: 'QuerySet[Transaction]' = self.transactions.filter(
            posted_date = transaction.posted_date
        )

        for potential_duplicate in same_posted_day_transactions:
            duplicate_suspicion = 0
            
            # Check amount
            abs_transaction_credit_amount = abs(transaction.credit_amount)
            abs_transaction_debit_amount = abs(transaction.debit_amount)
            potential_duplicate_amount = potential_duplicate.readable_amount()
            
            # It's a Credit
            if potential_duplicate_amount > 0:
                if abs(abs_transaction_credit_amount - potential_duplicate_amount) < .05: duplicate_suspicion += 2

            # It's a Debit. Multiply by -1 so we ensure both sides of the subtraction are positive
            else:
                if abs(abs_transaction_debit_amount - potential_duplicate_amount*-1) < .05: duplicate_suspicion += 2

            # Check description
            if transaction.description == potential_duplicate.description: duplicate_suspicion += 3

            # Check category
            if transaction.category == potential_duplicate.category: duplicate_suspicion += 1
            if duplicate_suspicion > 4: break

        if duplicate_suspicion > 4:
            return True
        else:
            return False
        

    def import_transactions_from_template(self, transactions: list[TransactionTemplate]) -> tuple[bool, list[str]]:
        transactions_imported = 0
        transactions_skipped = []
        
        # Make sure we haven't already processed the transaction
        for tr in transactions:
            if (self._is_duplicate_transaction(tr)):
                transactions_skipped.append(tr)
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

        TransactionTemplate.export_to_csv(transactions_skipped)

        if transactions_imported == 0: return (False,[f"No transactions were imported. {len(transactions_skipped)} transactions were skipped"])

        return (True,[f"{len(transactions_skipped)} transaction(s) were skipped.\n{transactions_imported} transaction(s) were imported to {self}."])
    
    def __str__(self) -> str:
        return f"Account: {self.name}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name="items")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(default="")
    category = models.CharField(max_length=255,default="", blank=True)
    category_certainty = models.FloatField(blank=True, null=True)
    _itemized_from = models.ForeignKey('TransactionItem',on_delete=models.SET_NULL,null=True,default=None,blank=True,editable=False)

    tags = TaggableManager(blank=True)

    def readable_amount(self):
        if self.amount < 0:
            self.amount = abs(self.amount)
            self.save(update_fields=["amount",])

        if self.transaction.is_credit(): 
            return self.amount
        return self.amount*-1
    
    def __str__(self) -> str:
        if len(self.description) > 40:
            return f"{self.description[:40]} | $ {self.readable_amount()}" 
        
        return f"{self.description} | $ {self.readable_amount()}"

class Transaction(models.Model):
    transaction_date = models.DateField(blank=True)
    posted_date = models.DateField(blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    description = models.TextField(default="")
    category = models.CharField(max_length=255, blank=True)
    category_certainty = models.FloatField(blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.00)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.00)

    note = models.TextField(blank=True,default="")

    tags = TaggableManager(blank=True)

    # If the balance is not given for a transaction, null
    balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True,null=True, default=None)

    def is_credit(self):
        return True if self.credit_amount > 0 else False

    def readable_amount(self):
        if abs(self.debit_amount) > 0:
            return abs(self.debit_amount)*-1
        if abs(self.credit_amount) > 0:
            return abs(self.credit_amount)
        return Decimal(0)
    readable_amount.short_description="Amount"



@receiver(post_save, sender=Transaction)
def _create_default_transaction_items(sender: 'Transaction', instance: 'Transaction', created: bool, raw: bool, using, update_fields, **kwargs):
        if not created:
            return
        
        if instance is None:
            raise Exception("No instance was created / provided")

        if instance.items.all().count() > 0:
            return

        item = TransactionItem(
            transaction = instance,
            amount = abs(instance.readable_amount()),
            description = instance.description,
            category = instance.category,
            category_certainty = instance.category_certainty
        )
        item.save()
        item.tags.add(*[tag for tag in instance.tags.all()])
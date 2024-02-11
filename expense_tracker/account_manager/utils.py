from typing import TYPE_CHECKING
from decimal import Decimal
from django.db.models import Sum,Q


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from .models import Transaction


def get_total_income_from_transactions(transactions: 'QuerySet[Transaction]'):
    # Account is NOT a Credit Card. 
    income_transactions = transactions.filter(~Q(account__type=2),credit_amount__gt=0) 
    sum = income_transactions.aggregate(Sum("credit_amount"))
    total = sum["credit_amount__sum"] if sum["credit_amount__sum"] is not None else Decimal(0)
    
    return total

def get_total_expenses_from_transactions(transactions: 'QuerySet[Transaction]'):
    sum = transactions.aggregate(Sum("debit_amount"))["debit_amount__sum"]

    return abs(sum) if sum is not None else Decimal(0)
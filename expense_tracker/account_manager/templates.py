from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class TransactionTemplate:
    transaction_date: date
    posted_date: date
    description: str
    category: str
    debit_amount: Decimal
    credit_amount: Decimal
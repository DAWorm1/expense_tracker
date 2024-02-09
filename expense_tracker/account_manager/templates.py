from dataclasses import dataclass,fields
from datetime import date
from decimal import Decimal
import os
import csv

@dataclass
class TransactionTemplate:
    transaction_date: date
    posted_date: date
    description: str
    category: str
    debit_amount: Decimal
    credit_amount: Decimal

    @classmethod
    def export_to_csv(cls, transactions: 'list[TransactionTemplate]', filename = "skipped_transactions.csv"):
        if os.path.isfile(filename):
            mode = "a"
        else:
            mode = "w"
        
        with open(filename,mode) as f:
            writer = csv.writer(f)
            columns = []
            for field in fields(cls):
                columns.append(field.name)


            for tr in transactions:
                _ = []
                for col in columns:
                    _.append(getattr(tr,col))

                writer.writerow(_)
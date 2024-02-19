from typing import TYPE_CHECKING
from decimal import Decimal
from django.db.models import Sum,Q
import subprocess
from django.conf import settings
from dotenv import load_dotenv
import os
import logging
import threading

load_dotenv()


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


def start_django_admin_subprocess(name_of_command, args=[], exec_on_exit=None):
    def run_in_thread(on_exit=None):
        proc = subprocess.Popen(
            [python_path, settings.BASE_DIR / "manage.py", name_of_command] + args
        )
        proc.wait()
        if exec_on_exit is not None:
            exec_on_exit()
        return
    
    python_path = os.environ.get("ET_PYTHON_PATH") 
    if python_path is None:
        raise Exception("Could not get the ET_PYTHON_PATH environment variable")
    print(python_path)

    logger = logging.getLogger("AI")
    logger.log(logging.DEBUG,f"Starting django-admin subprocess.\nCommand: {name_of_command}\nArguments: {args}")

    run_in_thread(exec_on_exit)


    

    
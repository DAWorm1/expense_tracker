from django.shortcuts import render
from .models import Transaction

# Create your views here.
def transaction_detail(request, id: int):
    tr = Transaction.objects.get(pk=id)

    context = {
        "readable_amount": tr.readable_amount(),
        "transaction_metadata": {
            "transaction_date": tr.transaction_date,
            "posted_date": tr.posted_date,
            "account": tr.account,
            "description": tr.description,
            "category": tr.category
        },
        "id": id
    }
    return render(request,"account_manager/transaction-detail.html",context=context)
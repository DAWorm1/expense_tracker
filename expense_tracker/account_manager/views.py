from django.shortcuts import render
from django.urls import reverse
from .models import Transaction
from .forms import EditableTransactionFields
from django.http.response import HttpResponseRedirect

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
        "id": id,
        "transaction": tr,
        "editable_transaction_fields": EditableTransactionFields(instance=tr)
    }
    return render(request,"account_manager/transaction-detail.html",context=context)

def transaction_edit(request, id: int):
    tr = Transaction.objects.get(pk=id)
    made_changes = False

    if request.POST.get("description"):
        tr.description = request.POST["description"]
        made_changes = True
    if request.POST.get("category"):
        tr.category = request.POST["category"]
        tr.category_certainty = 1
        made_changes = True
    if request.POST.get("tags"):
        for tag in request.POST.get("tags").split(","):
            tr.tags.add(tag)
        
        made_changes = True
        
    if made_changes:
        tr.save()

    return HttpResponseRedirect(reverse("account_manager:transaction-detail",args=[id]))
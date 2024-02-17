from django.shortcuts import render
from django.urls import reverse
from .models import Transaction, TransactionItem
from .forms import EditableTransactionFields, TransactionItemDetailForm
from django.http.response import HttpResponseRedirect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http.request import HttpRequest

def _get_transaction_detail_context(tr: Transaction, form: TransactionItemDetailForm|None = None):
    if form is None:
        new_item_form = TransactionItemDetailForm(tr)
    else:
        new_item_form = form
    
    new_item_start_hidden = True if form is None else False

    context = {
        "readable_amount": tr.readable_amount(),
        "transaction_metadata": {
            "transaction_date": tr.transaction_date,
            "posted_date": tr.posted_date,
            "account": tr.account,
            "description": tr.description,
            "category": tr.category
        },
        "id": tr.pk,
        "transaction": tr,
        "editable_transaction_fields": EditableTransactionFields(instance=tr),
        "new_item_form": new_item_form,
        "new_item_start_hidden": new_item_start_hidden
    }
    return context

# Create your views here.
def transaction_detail(request, id: int):
    tr = Transaction.objects.get(pk=id)

    context = _get_transaction_detail_context(tr)
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
    if request.POST.get("amount"):
        if tr.is_credit():
            tr.credit_amount = request.POST.get("amount")
        else:
            tr.debit_amount = request.POST.get("amount")
        made_changes = True
        
    if made_changes:
        tr.save()

    return HttpResponseRedirect(reverse("account_manager:transaction-detail",args=[id]))

def transaction_item_create(request: 'HttpRequest', id: int):
    tr = Transaction.objects.get(pk=id)

    form = TransactionItemDetailForm(tr,request.POST)
    if not form.is_valid():
        return render(
            request,
            "account_manager/transaction-detail.html",
            context=_get_transaction_detail_context(tr,form))
    
    clean_data = form.cleaned_data
    
    if clean_data.get("amount") is None:
        raise Exception("Could not get amount")
    if clean_data.get("description") is None:
        raise Exception("Could not get description")
    
    tr_item_fields = {
        "amount":None,
        "description":None,
        "category":None,
        "category_certainty":None,
        "transaction": None,
    }
    
    # Get all the required fields from the Form
    for field, value in clean_data.items():
        if field in tr_item_fields.keys():
            if field=="amount":
                print(value)
            if field=="subtract_from_transaction":
                continue
            tr_item_fields[field] = value

    # Set up the relationship
    tr_item_fields["transaction"] = tr
    
    # Check for the optional fields
    if tr_item_fields["category"] in [None,""]:
        tr_item_fields["category"] = ""
        tr_item_fields["category_certainty"] = 0
    else:
        # A category was given when creating this item. We are 100% certain of the accuracy of this category
        tr_item_fields["category_certainty"] = 1

    tr_item = TransactionItem(**tr_item_fields)

    # Set up connection between new TransactionItem and TransactionItem that it is being itemized off of. 
    subtract_tr_item = clean_data.get("subtract_from_transaction")
    assert isinstance(subtract_tr_item, TransactionItem)
    tr_item._itemized_from=subtract_tr_item
    subtract_tr_item.amount-=tr_item.amount
    
    tr_item.save()
    subtract_tr_item.save(update_fields=["amount",])    

    return HttpResponseRedirect(reverse("account_manager:transaction-detail", args=[id]))

def transaction_item_delete(request: 'HttpRequest', id: int, item_id: int):
    tr_item = TransactionItem.objects.get(pk=item_id)  
    tr = Transaction.objects.get(pk=id)
    subtraction_item = None

    if tr_item._itemized_from is not None:
        subtraction_item = tr_item._itemized_from
    else:
        subtraction_item:'TransactionItem' = tr.items.all()[0]
        i = 1
        while subtraction_item.pk == tr_item.pk:
            if tr.items.all().count() > i:
                subtraction_item = tr.items.all()[i]
                i += 1

    subtraction_item.amount += tr_item.amount
    subtraction_item.save(update_fields=["amount",])
    tr_item.delete()

    return HttpResponseRedirect(reverse("account_manager:transaction-detail", args=[id]))
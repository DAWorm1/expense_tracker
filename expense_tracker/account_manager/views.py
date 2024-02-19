from django.shortcuts import render
from django.urls import reverse
from .models import Transaction, TransactionItem
from django.db.models import Sum
from .forms import EditableDebitTransactionForm,EditableCreditTransactionForm,TransactionItemDetailForm
from .filters import Category
from django.http.response import HttpResponseRedirect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http.request import HttpRequest

def _get_transaction_detail_context(tr: Transaction, new_item_form_post: TransactionItemDetailForm|None = None, editable_transaction_form_post: EditableDebitTransactionForm|EditableCreditTransactionForm|None = None):
    if new_item_form_post is None:
        new_item_form = TransactionItemDetailForm(tr)
    else:
        new_item_form = new_item_form_post

    if editable_transaction_form_post is None:

        editable_transaction_form = EditableCreditTransactionForm(instance=tr) if tr.is_credit() else EditableDebitTransactionForm(instance=tr) 
    else:
        editable_transaction_form = editable_transaction_form_post
    
    new_item_start_hidden = True if new_item_form_post is None else False

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
        "editable_transaction_fields": editable_transaction_form,
        "new_item_form": new_item_form,
        "new_item_start_hidden": new_item_start_hidden
    }
    return context

def category_detail(request, name:str):
    context = {
        "name": name
    }

    context["category_transactions"] = Transaction.objects.filter(category=name)

    return render(request,"account_manager/category-detail.html",context=context)

# Create your views here.
def category_index(request):
    context = {}

    all_categories: list[str] = [cat["category"] for cat in Transaction.objects.all().order_by("category").values("category").distinct()]

    # Get data for each category and create Category objects to send to Template
    category_filters = {}
    for cat in all_categories:
        all_tr = Transaction.objects.filter(category=cat)
        credit_amount = all_tr.aggregate(Sum("credit_amount"))["credit_amount__sum"]
        debit_amount = all_tr.aggregate(Sum("debit_amount"))["debit_amount__sum"]
        amount = credit_amount - debit_amount
        
        verified_transactions = 0
        for tr in all_tr:
            if tr.is_category_verified():
                verified_transactions += 1
        
        category_filters[cat] = Category(
            tr.category,
            amount,
            all_tr.count(),
            verified_transactions)

    context["category_filters"] = sorted(category_filters.values(), key=lambda x: x.amount)

    return render(request,"account_manager/category-index.html", context=context)


def transaction_detail(request, id: int):
    tr = Transaction.objects.get(pk=id)

    context = _get_transaction_detail_context(tr)
    return render(request,"account_manager/transaction-detail.html",context=context)

def transaction_item_create(request: 'HttpRequest', id: int):
    tr = Transaction.objects.get(pk=id)

    form = TransactionItemDetailForm(tr,request.POST)
    if not form.is_valid():
        return render(
            request,
            "account_manager/transaction-detail.html",
            context=_get_transaction_detail_context(tr,new_item_form_post=form))
    
    clean_data = form.cleaned_data
    
    if clean_data.get("amount") is None:
        raise Exception("Could not get amount")
    if clean_data.get("description") is None:
        raise Exception("Could not get description")
    
    tr_item_fields = {
        "amount":None,
        "description":None,
        "category":None,
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
from django.http.request import HttpRequest
from django.shortcuts import render
from .views import get_header_sorting_dict
from account_manager.filters import get_transactions_filter_by_period,Period,get_transactions_filter_by_date
from account_manager.forms import DateFilterForm
from django.db.models.functions import Abs

def change_sort(request: HttpRequest):
    context = {}

    sorting = get_header_sorting_dict()  
    col = request.GET.get("col")

    if col not in sorting.keys():
        raise Exception("The col clicked was not found in the sorting dictionary. Make sure the header name attribute and get_header_sorting_dict transaction_table_headers list match.")

    prev_order = request.GET.get("prev_order")

    if prev_order is None:
        sorting[col] = "asc"

    if prev_order == "asc": 
        sorting[col] = "desc"
    
    context["sorting"] = sorting

    transactions = None

    if request.GET.get("dashboard_filter_period"):
        filter_period = request.GET.get("dashboard_filter_period")
        if Period.is_period(filter_period):
            transactions = get_transactions_filter_by_period(Period[filter_period])

    if request.GET.get("start_date") or request.GET.get("end_date"):
       form = DateFilterForm(request.GET)
       if form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        transactions = get_transactions_filter_by_date(start_date,end_date)

    if transactions is None:
        raise Exception("We should have filtered by period (through redirection to THIS_MONTH) or by date (through date_filter form)")

    if col != "amount":
        sort_prefix = "-" if sorting[col] == "desc" else ""
        context["transactions"] = transactions.order_by(sort_prefix+col)
    else:
        transactions = transactions.annotate(debit_amount_abs=Abs("debit_amount"))
        if sorting[col] == "desc":
            context["transactions"] = transactions.order_by("-debit_amount_abs")
        else:
            context["transactions"] = transactions.order_by().order_by("-credit_amount")

    return render(request,"transaction_table.html",context=context)
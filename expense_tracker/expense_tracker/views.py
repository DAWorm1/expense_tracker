from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http.request import HttpRequest
from account_manager.filters import Period,get_transactions_filter_by_period,get_transactions_filter_by_date
from account_manager.utils import get_total_income_from_transactions,get_total_expenses_from_transactions
from account_manager.forms import DateFilterForm

def get_header_sorting_dict():
    # Set up transaction table sorting
    transaction_table_headers = ["transaction_date", "description", "account", "amount", "category", "category_certainty"]
    sorting = {}

    for header in transaction_table_headers:
        sorting[header] = None

    return sorting

def index(request: HttpRequest):
    context = {}

    if not request.user.is_authenticated:
        return render(request,"index.html",context)

    def get_stats_from_transactions(transactions, context):
        context["total_income"] = get_total_income_from_transactions(transactions)
        context["total_expenses"] = get_total_expenses_from_transactions(transactions)
        context["net"] = context["total_income"] - context["total_expenses"]
        context["transactions"] = transactions
        
        return context
    
    def finalize_request_and_render(request,context,transactions,start_date,end_date,template="index.html"):
        context = get_stats_from_transactions(transactions,context)
        context["dateFilterForm"] = DateFilterForm(initial={
            "start_date": start_date,
            "end_date": end_date
        })

        return render(request,template,context)
    
    # Set up available filter periods
    context["available_periods"] = [e for e in Period]
    context["sorting"] = get_header_sorting_dict()

    # Set the sorting dictionary so that the CSS displays accordingly
    context["sorting"]['transaction_date']="desc"

    # Handle Custom date filter, if present
    if request.GET.get("start_date") or request.GET.get("end_date"):
        form = DateFilterForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            transactions = get_transactions_filter_by_date(start_date,end_date).order_by("-transaction_date")
        
            return finalize_request_and_render(request,context,transactions,start_date,end_date)
            
    # Force some filtering for the dashboard. If none, default to this month
    if not request.GET.get("dashboard_filter_period"):
        return HttpResponseRedirect(reverse("index")+f"?dashboard_filter_period={Period.THIS_MONTH.name}",)

    # Use one of the predefined periods
    dashboard_filter_period = request.GET.get("dashboard_filter_period")

    if (Period.is_period(dashboard_filter_period)):
        p = Period[dashboard_filter_period]
        transactions = get_transactions_filter_by_period(p).order_by("-transaction_date")
        start_date,end_date = Period.get_start_end_date_of_period(p)
        return finalize_request_and_render(request,context,transactions,start_date,end_date)
    

    raise Exception("We should not have arrived to this part of the code. The view should've redirected the user back to a period of THIS_MONTH")

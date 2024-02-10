from django.shortcuts import render
from django.http.response import HttpResponseRedirect,HttpResponse
from django.http.request import HttpRequest
from account_manager.filters import Period,get_transactions_filter_by_period
from account_manager.utils import get_total_income_from_transactions,get_total_expenses_from_transactions

def index(request: HttpRequest):
    context = {}

    if not request.user.is_authenticated:
        return render(request,"index.html",context)
    
    # Set up available filter periods
    available_periods = [e for e in Period]
    context["available_periods"] = available_periods

    if request.GET.get("dashboard_filter_period"):
        dashboard_filter_period = request.GET.get("dashboard_filter_period")
        if (Period.is_period(dashboard_filter_period)):
            p = Period[dashboard_filter_period]
            transactions = get_transactions_filter_by_period(p)

            context["total_income"] = get_total_income_from_transactions(transactions)
            context["total_expenses"] = get_total_expenses_from_transactions(transactions)

    return render(request,"index.html",context)
    
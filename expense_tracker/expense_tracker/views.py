from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponseRedirect,HttpResponse
from django.http.request import HttpRequest
from account_manager.filters import Period,get_transactions_filter_by_period
from account_manager.utils import get_total_income_from_transactions,get_total_expenses_from_transactions
from account_manager.forms import DateFilterForm
from account_manager.models import Transaction

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
    
    # Set up available filter periods
    context["available_periods"] = [e for e in Period]

    # Handle Custom date filter
    if request.method == "POST":
        form = DateFilterForm(request.POST)
        if form.is_valid():
            s_d = form.cleaned_data["start_date"]
            e_d = form.cleaned_data["end_date"]

            transactions = Transaction.objects.filter(
                transaction_date__gte=s_d,
                transaction_date__lte=e_d
            ).order_by("-transaction_date")

            context = get_stats_from_transactions(transactions,context)
            context["dateFilterForm"] = DateFilterForm(initial={
                "start_date": s_d,
                "end_date": e_d
            })

            return render(request,"index.html",context)
    # Use one of the predefined periods
    else:
        # Force some filtering for the dashboard. If none, default to this month
        if not request.GET.get("dashboard_filter_period"):
            return HttpResponseRedirect(reverse("index")+f"?dashboard_filter_period={Period.THIS_MONTH.name}",)

        dashboard_filter_period = request.GET.get("dashboard_filter_period")
        if (Period.is_period(dashboard_filter_period)):
            p = Period[dashboard_filter_period]
            transactions = get_transactions_filter_by_period(p).order_by("-transaction_date")
            context = get_stats_from_transactions(transactions,context)
            # Put this periods' dates into the date filter form
            start_date,end_date = Period.get_start_end_date_of_period(p)
            context["dateFilterForm"] = DateFilterForm(initial={
                "start_date": start_date,
                "end_date": end_date
            })

    return render(request,"index.html",context)

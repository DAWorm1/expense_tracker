from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Transaction

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_filter=['account',]
    list_display=['transaction_date','description','debit_amount','category']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        return qs.filter(debit_amount__gt=0)

admin.site.register(Transaction, TransactionAdmin)
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Transaction,Account

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_filter=['account',]
    list_display=['transaction_date','description','readable_amount','category']
    
class AccountAdmin(admin.ModelAdmin):
    pass


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
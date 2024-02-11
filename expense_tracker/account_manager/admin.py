from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Transaction,Account,TransactionItem

# Register your models here.

class TransactionItemInlineAdmin(admin.TabularInline):
    model = TransactionItem
    extra = 0 

class TransactionAdmin(admin.ModelAdmin):
    list_filter=['account',]
    list_display=['transaction_date','description','readable_amount','category']
    inlines = [
        TransactionItemInlineAdmin,
    ]
    
class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
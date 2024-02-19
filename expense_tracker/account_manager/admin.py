from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import Transaction,Account,TransactionItem
from .utils import start_django_admin_subprocess
from django.core.management import call_command
from django.conf import settings
import subprocess

# Register your models here.

class TransactionItemInlineAdmin(admin.TabularInline):
    model = TransactionItem
    extra = 0 

@admin.action()
def get_vendors(modeladmin, request, queryset):
    ids = []
    for tr in queryset:
        ids.append(tr.pk)
    
    start_django_admin_subprocess(
        "get_vendor_name_from_transaction_description",
        [str(id) for id in ids]
    )

    # call_command("get_vendor_name_from_transaction_description",*ids)
    modeladmin.message_user(request,f"Getting the vendors for {len(ids)} Transaction(s)")


class TransactionAdmin(admin.ModelAdmin):
    list_filter=['account',"vendor"]
    list_display=['transaction_date','description','readable_amount','category','vendor']
    inlines = [
        TransactionItemInlineAdmin,
    ]
    fields = [
        "transaction_date",
        "posted_date",
        ("is_vendor_verified",
        "is_category_verified"),
        "account",
        "description",
        "category",
        "debit_amount",
        "credit_amount",
        "vendor",
    ]
    readonly_fields = [
        "is_vendor_verified",
        "is_category_verified"
    ]
    actions = [get_vendors]
    
   
    
class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
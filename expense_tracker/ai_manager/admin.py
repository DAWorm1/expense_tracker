from django.contrib import admin
from .models import GetVendor_AIModel


# Register your models here.
@admin.register(GetVendor_AIModel)
class GetVendor_AIModel_Admin(admin.ModelAdmin):
    pass
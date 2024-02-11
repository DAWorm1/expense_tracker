from django.urls import path, include
from .views import transaction_detail

app_name = "account_manager"

urlpatterns = [
    path('<int:id>',transaction_detail,name="transaction-detail"),
]
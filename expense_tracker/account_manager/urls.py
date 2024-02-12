from django.urls import path, include
from .views import transaction_detail,transaction_edit

app_name = "account_manager"

urlpatterns = [
    path('<int:id>',transaction_detail,name="transaction-detail"),
    path('<int:id>/edit/',transaction_edit,name="transaction-edit")
]
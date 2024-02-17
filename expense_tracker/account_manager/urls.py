from django.urls import path, include
from .views import transaction_detail,transaction_edit,transaction_item_create,transaction_item_delete

app_name = "account_manager"

urlpatterns = [
    path('transaction/<int:id>',transaction_detail,name="transaction-detail"),
    path('transaction/<int:id>/edit/',transaction_edit,name="transaction-edit"),
    path('transaction/<int:id>/item/add/',transaction_item_create,name="transaction-item-add"),
    path('transaction/<int:id>/item/<int:item_id>/delete', transaction_item_delete,name='transaction-item-delete')
]
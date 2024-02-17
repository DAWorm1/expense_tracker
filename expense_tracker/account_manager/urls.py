from django.urls import path, include
from .views import transaction_detail,transaction_edit,transaction_item_create,transaction_item_delete

app_name = "account_manager"

urlpatterns = [
    path('<int:id>',transaction_detail,name="transaction-detail"),
    path('<int:id>/edit/',transaction_edit,name="transaction-edit"),
    path('<int:id>/item/add/',transaction_item_create,name="transaction-item-add"),
    path('<int:id>/item/<int:item_id>/delete', transaction_item_delete,name='transaction-item-delete')
]
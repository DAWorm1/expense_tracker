from django.urls import path, include
from .views import transaction_detail,transaction_item_create,transaction_item_delete,category_index,category_detail
from .views_htmx import transaction_edit



app_name = "account_manager"

urlpatterns = [
    path('category/',category_index,name='category-index'),
    path('category/<str:name>',category_detail,name='category-detail'),
    path('transaction/<int:id>',transaction_detail,name="transaction-detail"),
    path('transaction/<int:id>/item/add/',transaction_item_create,name="transaction-item-add"),
    path('transaction/<int:id>/item/<int:item_id>/delete', transaction_item_delete,name='transaction-item-delete')
]

htmxpatterns = [
    path('transaction/<int:id>/edit/',transaction_edit,name="transaction-edit"),
]

urlpatterns += htmxpatterns
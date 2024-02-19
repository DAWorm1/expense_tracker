from .models import Transaction
from .forms import EditableCreditTransactionForm,EditableDebitTransactionForm
from .utils import start_django_admin_subprocess
from django.shortcuts import render

def transaction_edit(request, id: int):
    tr = Transaction.objects.get(pk=id)
    
    form = EditableCreditTransactionForm(request.POST, instance=tr) if tr.is_credit() else EditableDebitTransactionForm(request.POST, instance=tr)

    context = {
        "transaction": tr
    }
    
    if form.is_valid():
        if "category" in form.changed_data:
            print("We changed the category")
            form.instance.set_category(form.cleaned_data["category"])
        if "vendor" in form.changed_data:
            print("We changed the vendor")
            form.instance.set_vendor(form.cleaned_data["vendor"])
            start_django_admin_subprocess(
                "add_item_to_vendor_database",
                [tr.description,form.cleaned_data["vendor"]]
            )
        
        form.save()

        context["editable_transaction_fields"] = EditableCreditTransactionForm(instance=tr) if tr.is_credit() else EditableDebitTransactionForm(instance=tr)
        return render(request,"account_manager/transaction_editable_fields.html",context=context)
    else:
        context["editable_transaction_fields"] = form
        return render(request,"account_manager/transaction_editable_fields.html",context=context)
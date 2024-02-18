from .models import Transaction
from .forms import EditableCreditTransactionForm,EditableDebitTransactionForm
from django.shortcuts import render

def transaction_edit(request, id: int):
    tr = Transaction.objects.get(pk=id)
    
    form = EditableCreditTransactionForm(request.POST, instance=tr) if tr.is_credit() else EditableDebitTransactionForm(request.POST, instance=tr)

    context = {
        "transaction": tr
    }
    
    if form.is_valid():
        form.save()
        context["editable_transaction_fields"] = EditableCreditTransactionForm(instance=tr) if tr.is_credit() else EditableDebitTransactionForm(instance=tr)
        return render(request,"account_manager/transaction_editable_fields.html",context=context)
    else:
        context["editable_transaction_fields"] = form
        return render(request,"account_manager/transaction_editable_fields.html",context=context)
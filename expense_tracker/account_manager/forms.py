from django.forms import forms,fields
from django import forms as dForms
from django.core.exceptions import ValidationError
from .models import Transaction,TransactionItem
from typing import Any

class DateInput(dForms.DateInput):
    input_type = 'date'

class DateFilterForm(forms.Form):
    start_date = fields.DateField(label="Start Date",widget=DateInput)
    end_date = fields.DateField(label="End Date",widget=DateInput)

class BaseHiddenForm(dForms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'hidden'

class EditableTransactionFields(BaseHiddenForm):
    class Meta:
        model = Transaction
        fields = ["description", "category", "tags"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['amount'] = dForms.DecimalField(max_digits=15,decimal_places=2)
        self.fields['amount'].widget.attrs['class'] = 'hidden'

        instance: 'Transaction' = kwargs.get("instance")

        if instance is None:
            return 
        
        amount = abs(instance.credit_amount) if instance.is_credit() else abs(instance.debit_amount)

        self.fields['amount'].initial = amount

class TransactionItemDetailForm(dForms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ["amount","description","category"]

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()

        subtract_item = cleaned.get("subtract_from_transaction")
        assert isinstance(subtract_item,TransactionItem)
        amount = cleaned.get("amount")

        if subtract_item is None:
            self.add_error("subtract_from_transaction", ValidationError("No item was given to subtract the amount from"))
        if amount is None:
            self.add_error("amount", ValidationError("No amount was given"))
        if subtract_item.amount < amount:
            self.add_error("amount", ValidationError("Cannot itemize the given TransactionItem. The amount to itemize is larger than the TransactionItem that is being itemized."))
        
        return cleaned

    def __init__(self, transaction: 'Transaction', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subtract_from_transaction"] = dForms.ModelChoiceField(TransactionItem.objects.filter(transaction=transaction),required=True)

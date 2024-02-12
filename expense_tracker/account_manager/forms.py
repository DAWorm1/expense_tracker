from django.forms import forms,fields
from django import forms as dForms
from .models import Transaction,TransactionItem

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
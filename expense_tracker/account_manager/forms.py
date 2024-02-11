from django.forms import forms,fields
from django import forms as dForms

class DateInput(dForms.DateInput):
    input_type = 'date'

class DateFilterForm(forms.Form):
    start_date = fields.DateField(label="Start Date",widget=DateInput)
    end_date = fields.DateField(label="End Date",widget=DateInput)

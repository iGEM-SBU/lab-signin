from django import forms
from django.forms import DecimalField


class HoursForm(forms.Form):
    hours = DecimalField(min_value=0, max_value=12, max_digits=4, decimal_places=2)

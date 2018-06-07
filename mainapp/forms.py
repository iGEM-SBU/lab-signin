from django import forms
from django.forms import DecimalField, TimeField


class HoursForm(forms.Form):
    hours = DecimalField(min_value=0, max_value=12, max_digits=4, decimal_places=2)


class SignInTimeForm(forms.Form):
    time_signed_in = TimeField(widget=forms.TimeInput(format="%H:%M"), label='What time did you come in (HH:MM)?')

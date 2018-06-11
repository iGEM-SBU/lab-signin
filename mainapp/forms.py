from django import forms
from django.forms import DecimalField, TimeField, DateField, CharField


class HoursForm(forms.Form):
    hours = DecimalField(min_value=0, max_value=12, max_digits=4, decimal_places=2)


class SignInTimeForm(forms.Form):
    time_signed_in = TimeField(widget=forms.TimeInput(format="%H:%M"), label='What time did you come in (HH:MM)?')


class TimelineForm(forms.Form):
    text = CharField(max_length=280, required=False)


class BigTimeCorrectionForm(forms.Form):
    date = DateField(widget=forms.DateInput(format="%M/%D"), label="What day did you come in (MM/DD)?")
    hours = DecimalField(min_value=0, max_value=12, max_digits=4, decimal_places=2, label="How many hours did you do?")

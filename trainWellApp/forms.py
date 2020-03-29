from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from trainWellApp.models import Booking


class BookingForm(ModelForm):
    name = forms.CharField(max_length=80)
    phone_number = forms.CharField(max_length=10)  # TODO django-phonenumber-field
    datetime_init = forms.DateTimeField()
    datetime_end = forms.DateTimeField()

    class Meta:
        model = Booking
        fields = ['name', 'phone_number', 'datetime_init', 'datetime_end']

    def clean_renewal_date(self):
        start = self.cleaned_data['datetime_init']
        end = self.cleaned_data['datetime_end']

        # Check date is not in past.
        if start > end:
            raise ValidationError('Invalid date')

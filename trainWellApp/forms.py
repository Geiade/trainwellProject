from datetime import datetime

from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from trainWellApp.models import Booking, Event


class BookingForm(ModelForm):

    class Meta:
        model = Booking
        fields = ['name', 'phone_number', 'event','datetime_init', 'datetime_end']


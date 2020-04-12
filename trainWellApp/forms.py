from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from trainWellApp.models import Booking, Event, Planner, Selection


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


class PlannerForm(ModelForm):
    over_18 = forms.BooleanField(required=True)

    class Meta:
        model = Planner
        fields = ('over_18',)
        

# Creation of a booking made in two steps.
class BookingForm1(ModelForm):

    class Meta:
        model = Booking
        fields = ['name', 'phone_number', 'event', 'planner']


class BookingForm2(ModelForm):
    datetime_init = forms.DateTimeField(required=False)

    class Meta:
        model = Selection
        fields = ['booking', 'place', 'datetime_init']

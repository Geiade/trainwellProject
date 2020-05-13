from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from trainWellApp.models import Booking, Event, Planner, Selection, Incidence, Place


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'A user exits with the same email',
                code='password_mismatch',
            )
        return email


class PlannerForm(ModelForm):
    over_18 = forms.BooleanField(required=True)
    is_staff = forms.BooleanField(required=False)
    is_gerent = forms.BooleanField(required=False)
    staff_code = forms.CharField(required=False)
    gerent_code = forms.CharField(required=False)

    class Meta:
        model = Planner
        fields = ('over_18', 'is_staff', 'staff_code', 'is_gerent', 'gerent_code')


# Creation of a booking made in two steps.
class BookingForm1(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BookingForm1, self).__init__(*args, **kwargs)
        self.fields['event'].required = True
        self.fields['event'].queryset = Event.objects.filter(is_deleted=False)

    class Meta:
        model = Booking
        fields = ['name', 'phone_number', 'event', 'planner']


class BookingForm2(ModelForm):
    datetime_init = forms.DateTimeField(required=False)

    class Meta:
        model = Selection
        fields = ['booking', 'place', 'datetime_init']


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'places', 'color']


class OwnAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = self.authenticate(username, password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None


class IncidenceForm(ModelForm):
    class Meta:
        model = Incidence
        fields = ['name', 'description', 'limit_date', 'disabled', 'places']


class PlaceForm(ModelForm):
    class Meta:
        model = Place
        fields = ['name', 'price_hour', 'available_from', 'available_until', 'description']

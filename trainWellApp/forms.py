from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django import forms
from trainWellApp.models import Booking, Event, Planner, Selection
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from trainWellApp.models import Booking, Planner


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean_password2(self):
        error_messages = {
            'password_mismatch': 'The two password fields did not match!',
            'duplicated_email': 'A user exits with the same email',
        }

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                error_messages['password_mismatch'],
                code='password_mismatch',
            )

        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            err = forms.ValidationError(
                error_messages['duplicated_email'],
                code='duplicated_email',
            )
            self.add_error('email', err)

        return password2


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

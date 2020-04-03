from django.urls import reverse

from django.db import transaction
from django.shortcuts import render, redirect
from trainWellApp.forms import PlannerForm, UserForm

from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from django.urls import reverse
from django.views.generic import ListView, DetailView
from trainWellApp.models import Booking


def index(request):
    return render(request, 'index.html')


def is_signed(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    return False


@transaction.atomic
def signup(request):
    signed = is_signed(request)

    if signed is not False:
        return signed

    if request.method == "POST":
        user_form = UserForm(request.POST)
        planner_form = PlannerForm(request.POST)

        if user_form.is_valid() and planner_form.is_valid():
            user = user_form.save()
            instance = planner_form.save(commit=False)
            instance.user = user
            instance.save()
            return redirect(reverse('index'))

    else:
        user_form = UserForm()
        planner_form = PlannerForm()

    args = {'user_form': user_form, 'planner_form': planner_form}
    return render(request, 'accounts/signup.html', args)


def signin(request):
    '''signed = is_signed(request)

    if signed is not False:
        return signed'''

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                do_login(request, user)
                redirect(reverse('trainWellApp:dashboard'))
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/signin.html', {'form': form})


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Dashboard(ListView):
    model = Booking
    PAGINATE_BY = 20
    template_name = 'trainWellApp/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs

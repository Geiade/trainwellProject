from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as do_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView

from trainWellApp.models import Booking, Planner
from trainWellApp.forms import OwnAuthenticationForm
from trainWellApp.forms import PlannerForm, UserForm, BookingForm


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
        form = OwnAuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = form.authenticate(username=username, password=password)

            if user is not None:
                do_login(request, user)
                redirect(reverse('trainWellApp:dashboard'))
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/signin.html', {'form': form})


@login_required(login_url="/login/")
def booking_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            user = get_object_or_404(Planner, Q(id=request.user.id))
            book.user = user
            book.save()
            return redirect('trainwell:index')
    else:
        form = BookingForm()
    return render(request, 'add_book.html', context={'BookingForm': form})


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def bookingcancelation(request, pk):
    # Make booking deleted and turn availability on

    booking_query = Booking.objects.filter(pk=pk, planner__user_id=request.user.id)
    if booking_query.exists():
        booking = booking_query.first()
        booking.is_deleted = True
        booking.save()
    else:
        return Http404

    return redirect(reverse('trainWellApp:dashboard'))


class Dashboard(ListView):
    model = Booking
    PAGINATE_BY = 20
    template_name = 'trainWellApp/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = self.model.objects.filter(is_deleted=False)
        return qs

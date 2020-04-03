from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, DetailView
from trainWellApp.models import Booking


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
                redirect(reverse('index'))
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

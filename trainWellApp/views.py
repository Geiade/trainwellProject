
from django.contrib.auth import authenticate
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse


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

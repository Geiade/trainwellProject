from django.urls import reverse

from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from trainWellApp.forms import PlannerForm, UserForm


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

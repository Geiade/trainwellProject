from django.shortcuts import render, redirect
from django.urls import reverse

from trainWellApp.forms import EventForm


def addEvent(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event_form.save()
            return redirect(reverse('trainwell:dashboard'))

    else:
        event_form = EventForm()

    args = {'event_form': event_form}
    return render(request, 'trainWellApp/add_event.html', args)

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView

from trainWellApp.forms import EventForm
from trainWellApp.models import Selection, Incidence


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


def _get_affected_bookings(init, end):
    selection = Selection.objects.filter(datetime_init__range=[init, end],
                                         booking__is_deleted=False)
    bookinglist = {}
    for s in selection:
        if s.booking in bookinglist:
            bookinglist[s.booking].append(s)
        else:
            bookinglist[s.booking] = [s]

    return bookinglist


class IncidencesListView(ListView):

    model = Incidence
    template_name = 'trainWellApp/incidences_list.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'done': self.get_queryset1()})
        return context


    def get_queryset(self):
        return self.model.objects.filter(done=False).order_by('limit_date')


    def get_queryset1(self):
        return self.model.objects.filter(done=True).order_by('limit_date')


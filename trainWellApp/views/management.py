from datetime import timedelta, datetime, date
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import json

from django.views.generic import ListView

from trainWellApp.forms import EventForm, IncidenceForm
from trainWellApp.models import Selection, Incidence, Place
from trainWellApp.views.trainwell import _generate_range, isajax_req


def addEvent(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event_form.save()
            return redirect(reverse('trainwell:dashboard'))

    else:
        event_form = EventForm()

    args = {'event_form': event_form}
    return render(request, 'staff/add_event.html', args)


def create_incidence(request):
    form = IncidenceForm()
    if request.method == "POST":
        form = IncidenceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['limit_date'] >= date.today():
                form.save()
                return redirect(reverse('trainwell:dashboard'))
    else:
        form = IncidenceForm()
    return render(request, 'staff/add_incidence.html', {'form': form})


class IncidencesListView(ListView):

    model = Incidence
    template_name = 'staff/incidences_list.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'done': self.get_queryset1()})
        return context


    def get_queryset(self):
        return self.model.objects.filter(done=False).order_by('limit_date')


    def get_queryset1(self):
        return self.model.objects.filter(done=True).order_by('limit_date')


# TO-DO owner on Incidence
def incidence_done(request, pk):
    incidence = Incidence.objects.get(pk=pk)
    incidence.done = True
    incidence.save()

    return redirect(reverse('staff:incidences_list'))


# View for head of facilities
class BookingListView(ListView):

    model = Selection
    template_name = 'staff/booking_list.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        day = self.get_day()
        range_day = Place.objects.filter(available_from__lt=day, available_until__gt=day).first()

        context.update({'next_day': (day + timedelta(days=1)).strftime("%d/%m/%Y"),
                        'prev_day': (day - timedelta(days=1)).strftime("%d/%m/%Y"),
                        'day': day,
                        'hours': _generate_range(range_day.available_from, range_day.available_until),
                        'isajax': isajax_req(self.request)})

        return context


    def get_queryset(self):
        bookings = {}
        day = self.get_day()
        selections = self.model.objects.filter(datetime_init__day=day.day, datetime_init__month=day.month,
                                               datetime_init__year=day.year, booking__is_deleted=False)

        for s in selections: bookings.setdefault(s.booking, []).append(s)

        return self.format_data(bookings)


    def get_day(self):
        ajax_data = self.request.GET.get('day')  # If ajax request, sends week.

        if ajax_data:
            day_list = ajax_data.split('/')
            day = datetime(int(day_list[2]), int(day_list[1]), int(day_list[0]))
        else:
            day = datetime.now()

        return day


    @staticmethod
    def format_data(bookings):
        # Sort first selections by hours.
        [v.sort(key=lambda x: x.datetime_init) for k, v in bookings.items()]

        for k, v in bookings.items():
            d = {}
            for e in v: d.setdefault(e.place.name, []).append(e.datetime_init.strftime("%H:%M"))
            bookings[k] = d

        return bookings


def affected_bookings_asjson(request):
    # Ajax data
    ajax_created = request.GET.get('created').split('-')
    ajax_limit_date = request.GET.get('limit_date').split('-')
    ajax_places = request.GET.get('places').split(',')

    init = datetime(int(ajax_created[0]), int(ajax_created[1]), int(ajax_created[2])).date()
    end = datetime(int(ajax_limit_date[0]), int(ajax_limit_date[1]), int(ajax_limit_date[2])).date()

    list_places = [int(place) for place in ajax_places if place]
    result = _get_affected_bookings(request, init, end, list_places)
    json_data = [(str(k.planner.user.first_name), str(k.planner.user.last_name),
                 str(k.event.name), str(k.phone_number), str(k.name)) for k, v in result.items()]

    return JsonResponse(json.dumps(json_data), safe=False)


def _get_affected_bookings(request, init, end, places):
    selection = Selection.objects.filter(datetime_init__range=[init, end],
                                         booking__planner__user_id=request.user.id,
                                         place_id__in=places,
                                         booking__is_deleted=False)
    bookinglist = {}
    for s in selection:
        if s.booking in bookinglist:
            bookinglist[s.booking].append(s)
        else:
            bookinglist[s.booking] = [s]

    return bookinglist

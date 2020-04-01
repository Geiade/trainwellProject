from datetime import timedelta, date, datetime
import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic.detail import DetailView
from isoweek import Week

from trainWellApp.models import Booking, Event


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def isajax_req(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def book(request):
    event = get_object_or_404(Event, Q(id=1))

    ajax_data = request.GET.get('week')  # If ajax request, sends week.
    week = _handle_ajax(ajax_data) if ajax_data else _get_week(datetime.now())

    opening_hours = [str(x) for x in range(9, 22)]

    booked_dates = _get_week_bookings(week)
    place_avail = _get_availability(event, week)
    weekdays = week.days()

    context = {'booked_dates': booked_dates,
               'place_avail': "e",
               'weekdays': weekdays,
               'hours': opening_hours,
               'next_week': (weekdays[0] + timedelta(days=7)).strftime("%d/%m/%Y"),
               'previous_week': (weekdays[0] - timedelta(days=7)).strftime("%d/%m/%Y"),
               'isajax': isajax_req(request),
               }

    return render(request, "dummy.html", context)


def _get_availability(event, week):

    to_month = date.today() + timedelta(days=30)

    place_avail = {}

    for place in event.places.all():
        if place.available_from.date() > to_month:
            continue

        place_avail[place] = [place.available_from.date(), place.available_until.date()]

    return place_avail


def _get_week_bookings(week):
    weekdays = [d.day for d in week.days()]
    months = [d.month for d in week.days()]
    bookings = Booking.objects.filter(datetime_init__day__in=weekdays,
                                      datetime_init__month__in=months,
                                      datetime_init__year=week.year)

    data = {}
    for b in bookings:
        data[b.name] = b.datetime_init.strftime("%A%X"), b.datetime_end.strftime("%A%X")

    return json.dumps(data)


def _get_week(day):
    return Week(day.year, day.isocalendar()[1])


def _handle_ajax(data):
    day_list = data.split('/')
    return _get_week(date(int(day_list[2]), int(day_list[1]), int(day_list[0])))
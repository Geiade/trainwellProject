import json
from datetime import timedelta, date, datetime
import numpy
import holidays
import pandas as pd
from django.db.models import Q
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

    week_avail, open_hours, public_days = _get_availability(event, week)
    weekdays = week.days()

    context = {'week_avail': week_avail,
               'weekdays': weekdays,
               'hours': open_hours,
               'next_week': (weekdays[0] + timedelta(days=7)).strftime("%d/%m/%Y"),
               'previous_week': (weekdays[0] - timedelta(days=7)).strftime("%d/%m/%Y"),
               'public_days': public_days,
               'isajax': isajax_req(request),
               }

    return render(request, "dummy.html", context)


def _get_availability(event, week):

    # Get event associated places
    all_places = event.places.all()

    weekdays = week.days()
    complete_week = 7 * len(all_places)
    week_avail, open_hours = {}, []

    # Get holidays, booked_dates and open hours for day.
    public_days = _get_public_days(week)
    booked_dates = _get_week_bookings(week)
    ranges = _get_places_ranges(event)
    dates_rng = ranges.keys()

    # We consider default opening hours from 9h to 21h
    def_rng = pd.date_range("9:00", "21:00", freq="H").strftime("%H:%M").tolist()

    # TO-DO incidències
    for d in weekdays:

        curr_rng = def_rng
        for rng in dates_rng:
            if rng[0] <= d <= rng[1]:
                open_hours.append(ranges.get(rng))
                curr_rng = ranges.get(rng)

        # No availability for holidays.
        if d in public_days.keys():
            [week_avail.update({d.strftime("%d/%m/%Y") + ',' + f.name: []}) for f in all_places]
            continue

        for f in all_places:
            bdate = booked_dates.get((f, d), None)

            if bdate:
                # Checked bookings to substract from availability
                booked_hours = pd.date_range(bdate[2].strftime("%H:%M"),
                                             bdate[3].strftime("%H:%M"),
                                             freq='H').strftime("%H:%M").tolist()

                booked_hours.pop()  # Notice is available since datetime_end.
                key = d.strftime("%d/%m/%Y") + ',' + f.name  # To serialize as JSON
                # Substract from range booked hours
                week_avail[key] = list(set(curr_rng) - set(booked_hours))
            else:
                key = d.strftime("%d/%m/%Y") + ',' + f.name
                week_avail[key] = curr_rng

        if len(week_avail) is complete_week: break


    return json.dumps(week_avail), open_hours, public_days



def _get_week_bookings(week):
    bookings = Booking.objects.filter(is_deleted=False)
    data = {}

    for b in bookings:
        if _get_week(b.datetime_init) == week:
            data[(b.place, b.datetime_init.date())] = b.name, b.place, b.datetime_init, b.datetime_end

    return data


def _get_week(day):
    return Week(day.year, day.isocalendar()[1])


def _get_places_ranges(event):
    """ Get availabilty of the sports center in a range of days. """
    ranges = {}

    for p in event.places.values():
        a_from, a_until = p.get('available_from'), p.get('available_until')

        # If already in dict, ignore
        if ranges.get((a_from.date(), a_until.date())): continue

        ranges[(a_from.date(), a_until.date())] = pd.date_range(a_from.strftime("%H:%M"),
                                                                a_until.strftime("%H:%M"),
                                                                freq='H').strftime("%H:%M").tolist()

    return ranges


def _get_public_days(week):
    # Holidays not available (Catalunya).
    public_days = holidays.ES(years=week.year, prov="CAT")
    week_pd = {}
    [week_pd.update({k: v}) for k, v in public_days.items() if _get_week(k) == week]
    return week_pd


def _handle_ajax(data):
    day_list = data.split('/')
    return _get_week(date(int(day_list[2]), int(day_list[1]), int(day_list[0])))

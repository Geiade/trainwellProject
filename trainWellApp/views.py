import json
from datetime import timedelta, date, datetime
import holidays
import pandas as pd
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.utils import timezone
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

    def_rng = _generate_range()

    # TO-DO incidències
    for d in weekdays:

        curr_rng = def_rng
        for rng in dates_rng:
            if rng[0] <= d <= rng[1]:
                open_hours.append(ranges.get(rng))
                curr_rng = ranges.get(rng)

        # No availability for holidays and weekdays lower today.
        now = datetime.now()
        hour_plus2 = (now + timedelta(hours=2)).replace(minute=00)
        if d in public_days.keys() or d < hour_plus2.date():
            [week_avail.update({d.strftime("%d/%m/%Y") + ',' + f.name: []}) for f in all_places]
            continue

        # Can book from now + 2 hours minimum.
        if d == now.date():
            _tonow = _generate_range(datetime(2020, 1, 1, int(curr_rng.pop(0).split(":")[0]), 00), hour_plus2)
            curr_rng = list(set(curr_rng) - set(_tonow))

        for f in all_places:
            bdate = booked_dates.get((f, d), None)

            if bdate:
                # Checked bookings to substract from availability
                booked_hours = _generate_range(bdate[2], bdate[3])
                booked_hours.pop()  # Notice is available since datetime_end.

                key = d.strftime("%d/%m/%Y") + ',' + f.name  # To serialize as JSON
                week_avail[key] = list(set(curr_rng) - set(booked_hours))  # Substract booked hours
            else:
                key = d.strftime("%d/%m/%Y") + ',' + f.name
                week_avail[key] = curr_rng

        if len(week_avail) is complete_week: break

    return json.dumps(week_avail), open_hours, public_days


def _get_week_bookings(week):
    end_week_date = week.days().pop()
    end_week_datetime = datetime(end_week_date.year, end_week_date.month, end_week_date.day)
    bookings = Booking.objects.filter(is_deleted=False, datetime_init__range=[timezone.now(),
                                                                              end_week_datetime])
    data = {}

    for b in bookings:
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
        ranges[(a_from.date(), a_until.date())] = _generate_range(a_from, a_until)

    return ranges


def _get_public_days(week):
    # Holidays not available (Catalunya).
    public_days = holidays.ES(years=week.year, prov="CAT")
    week_pd = {}
    [week_pd.update({k: v}) for k, v in public_days.items() if _get_week(k) == week]
    return week_pd


def _generate_range(fromm=datetime(2020, 1, 1, 9, 00), to=datetime(2020, 1, 1, 21, 00)):
    # Default date is dummy interested in hours.
    # We consider default opening hours from 9h to 21h.
    return pd.date_range(fromm.strftime("%H:%M"), to.strftime("%H:%M"),
                         freq='H').strftime("%H:%M").tolist()


def _handle_ajax(data):
    day_list = data.split('/')
    return _get_week(date(int(day_list[2]), int(day_list[1]), int(day_list[0])))

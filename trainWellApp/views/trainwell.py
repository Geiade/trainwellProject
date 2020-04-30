import json
from datetime import timedelta, date, datetime
import holidays
import pandas as pd

from formtools.wizard.views import NamedUrlSessionWizardView
from isoweek import Week

from django.db import transaction
from django.forms import formset_factory
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.conf import settings

from trainWellApp.models import Booking, Planner, Selection, Place
from trainWellApp.forms import OwnAuthenticationForm, PlannerForm, UserForm, BookingForm1, BookingForm2


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
            is_staff = False
            if planner_form.cleaned_data['is_staff'] is True:
                if planner_form.cleaned_data['staff_code'] == settings.STAFF_CODE:
                    is_staff = True
                else:
                    return redirect(reverse('index'))

            user = user_form.save()
            planner = planner_form.save(commit=False)
            planner.is_staff = is_staff
            planner.user = user
            planner.save()

        return redirect(reverse('index'))

    else:
        user_form = UserForm()
        planner_form = PlannerForm()

    args = {'user_form': user_form, 'planner_form': planner_form}
    return render(request, 'accounts/signup.html', args)


def signin(request):
    signed = is_signed(request)

    if signed is not False:
        return signed

    if request.method == "POST":
        form = OwnAuthenticationForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = form.authenticate(username=username, password=password)

            if user is not None:
                do_login(request, user)
                return redirect(reverse('trainwell:dashboard'))
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/signin.html', {'form': form})


# WizardView data
SelectionFormSet = formset_factory(BookingForm2, extra=15)
BOOK_FORMS = [("0", BookingForm1), ("1", SelectionFormSet)]
BOOK_TEMPLATES = {"0": 'trainWellApp/add_book.html',
                  "1": 'trainWellApp/availability.html'}


class BookingFormWizardView(NamedUrlSessionWizardView):

    def get_template_names(self):
        return [BOOK_TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        if self.steps.current == "1":
            event = self.get_cleaned_data_for_step('0')['event']

            ajax_data = self.request.GET.get('week')  # If ajax request, sends week.
            week = _handle_ajax(ajax_data) if ajax_data else _get_week(datetime.now())
            week_avail, open_hours, public_days = _get_availability(event, week)
            weekdays = week.days()

            context.update({'week_avail': week_avail,
                            'weekdays': weekdays,
                            'hours': open_hours,
                            'next_week': (weekdays[0] + timedelta(days=7)).strftime("%d/%m/%Y"),
                            'previous_week': (weekdays[0] - timedelta(days=7)).strftime("%d/%m/%Y"),
                            'public_days': public_days,
                            'isajax': isajax_req(self.request)})

        return context

    def get_form_step_data(self, form):
        form.data._mutable = True

        if self.steps.current == '0':
            planner = get_object_or_404(Planner, user_id=self.request.user.id)
            form.data['0-planner'] = planner.id

        elif self.steps.current == '1':
            json_data = self.request.POST['json_selection']
            selection = json.loads(json_data)
            i = 0

            for k, v in selection.items():
                for hour in v[0]:
                    d, m, y = v[1].split('/')
                    form.data['1-' + str(i) + '-datetime_init'] = y + '-' + m + '-' + d + ' ' + hour + ':00'
                    form.data['1-' + str(i) + '-place'] = (get_object_or_404(Place, id=int(k))).id
                    i += 1

            form.data.pop('json_selection')

        return form.data

    def done(self, form_list, **kwargs):

        booking = None

        for i, form in enumerate(form_list):
            if i == 0:
                booking = form.save()
                continue

            for selection in form:
                if selection.cleaned_data:
                    instance = selection.save(commit=False)
                    instance.booking = booking
                    instance.save()

        return redirect(reverse('trainwell:dashboard'))


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

    return redirect(reverse('trainwell:dashboard'))


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


def isajax_req(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


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
                open_hours.append(tuple(ranges.get(rng)))
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
            key = d.strftime("%d/%m/%Y") + ',' + f.name + ',' + str(f.id)   # To serialize as JSON
            week_avail[key], booked_hours = curr_rng, []

            for h in curr_rng:
                bdate = booked_dates.get((f, d, h), None)
                if bdate: booked_hours.append(bdate[2].strftime('%H:%M'))

            # Substract booked_hours
            week_avail[key] = list(set(week_avail[key]) - set(booked_hours))

        if len(week_avail) is complete_week: break

    return json.dumps(week_avail), open_hours, public_days


def _get_week_bookings(week):
    end_week_date, begin_week_date = week.days().pop(), week.days().pop(0)
    begin_week_datetime = datetime(begin_week_date.year, begin_week_date.month,
                                   begin_week_date.day, 00, 1, 00)
    end_week_datetime = datetime(end_week_date.year, end_week_date.month,
                                 end_week_date.day, 23, 59, 00)

    selections = Selection.objects.filter(datetime_init__range=[begin_week_datetime, end_week_datetime],
                                          booking__is_deleted=False)
    data = {}
    for s in selections: data[(s.place, s.datetime_init.date(), s.datetime_init.
                               strftime("%H:%M"))] = s.booking.name, s.place, s.datetime_init

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

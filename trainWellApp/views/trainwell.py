import json
from datetime import timedelta, date, datetime
import holidays
import pandas as pd
from django.views.generic.base import View
from formtools.wizard.views import NamedUrlSessionWizardView
from isoweek import Week

from django.db import transaction
from django.forms import formset_factory
from django.http import Http404
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.conf import settings

from trainWellApp.decorators import gerentstaff_required, gerent_required
from trainWellApp.models import Booking, Planner, Selection, Place, Notification, Invoice
from trainWellApp.forms import OwnAuthenticationForm, PlannerForm, UserForm, BookingForm1, BookingForm2
from trainWellApp.tasks import setup_task_ispaid, cancel_task, setup_task_event_done, notpaid_manager, \
    events_done_manager, setup_task_invoice
from trainWellApp.utils import Render


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
        print('Estas al signup')
        user_form = UserForm(request.POST)
        planner_form = PlannerForm(request.POST)

        print(user_form.errors)
        print(planner_form.errors)

        if user_form.is_valid() and planner_form.is_valid():
            is_staff = False
            is_gerent = False

            if planner_form.cleaned_data['is_staff'] is True:
                if planner_form.cleaned_data['staff_code'] == settings.STAFF_CODE:
                    is_staff = True
                else:
                    user_form = UserForm()
                    planner_form = PlannerForm()
                    args = {'user_form': user_form, 'planner_form': planner_form}
                    return render(request, 'accounts/signup.html', args)

            if planner_form.cleaned_data["is_gerent"] is True:
                if planner_form.cleaned_data['gerent_code'] == settings.GERENT_CODE:
                    is_gerent = True
                else:
                    user_form = UserForm()
                    planner_form = PlannerForm()
                    args = {'user_form': user_form, 'planner_form': planner_form}
                    return render(request, 'accounts/signup.html', args)

            user = user_form.save()
            planner = planner_form.save(commit=False)
            planner.is_staff = is_staff
            planner.is_gerent = is_gerent
            planner.user = user
            planner.save()

            return redirect(reverse('index'))

        else:
            user_form = UserForm(request.POST)
            planner_form = PlannerForm(request.POST)
            args = {'user_form': user_form, 'planner_form': planner_form}
            return render(request, 'accounts/signup.html', args)

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

                if user.is_superuser is True:
                    return redirect(reverse('trainwell:dashboard'))

                planner = Planner.objects.get(user=user)
                if planner.is_staff is True:
                    return redirect(reverse('staff:dashboard'))
                elif planner.is_gerent is True:
                    return redirect(reverse('manager:notifications_list'))
                else:
                    return redirect(reverse('trainwell:dashboard'))

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/signin.html', {'form': form})


def signout(request):
    do_logout(request)
    return redirect('/')


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
            # TODO, bug, event=none, when cancel add booking or accessing by url

            ajax_data = self.request.GET.get('week')  # If ajax request, sends week.
            if ajax_data:
                day_list = ajax_data.split('/')
                week = _get_week(date(int(day_list[2]), int(day_list[1]), int(day_list[0])))

            else:
                week = _get_week(datetime.now())

            week_avail, open_hours = _get_availability(event, week)
            weekdays = week.days()

            context.update({'week_avail': week_avail,
                            'weekdays': weekdays,
                            'hours': open_hours,
                            'next_week': (weekdays[0] + timedelta(days=7)).strftime("%d/%m/%Y"),
                            'previous_week': (weekdays[0] - timedelta(days=7)).strftime("%d/%m/%Y"),
                            'public_days': _get_public_days(week),
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

        # Create a notification for manager department.
        name = "New booking: " + booking.name
        description = booking.planner.user.username + " created new booking"
        Notification(name=name, description=description, level=2, booking=booking).save()

        setup_task_ispaid(booking)
        setup_task_event_done(booking)
        create_invoice(booking)

        return redirect(reverse('trainwell:dashboard'))


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_booking = context.get('booking')
        qs = Selection.objects.filter(booking_id=curr_booking.id).values('place_id', 'datetime_init')
        selections = {}

        for s in qs:
            place = Place.objects.get(id=s.get('place_id'))
            selections.setdefault(place, []).append(s.get('datetime_init'))

        context.update({'selections': selections})
        return context

@gerentstaff_required
def bookingcancelation(request, pk):
    # Make booking deleted and turn availability on

    booking_query = Booking.objects.filter(pk=pk, planner__user_id=request.user.id)
    if booking_query.exists():
        booking = booking_query.first()
        booking.is_deleted = True
        booking.save()

        # Create a notification for manager department.
        name = "Canceled booking: " + booking.name
        description = booking.planner.user.username + " has canceled a booking"
        Notification(name=name, description=description, level=2, booking=booking).save()

        qs = Invoice.objects.filter(booking_id=booking.id)
        if qs.exists():
            invoice = qs.first()
            state = invoice.booking_state

            if state == 1:
                event_date = booking.selection_set().all().first().datetime_init
                days_to_event = (event_date - datetime.now()).days

                # Booking canceled minimum 7 days in advance ('Cancelada pagada)
                invoice.booking_state = 3 if days_to_event >= 7 else 5

            else:
                invoice.booking_state = 4

            invoice.save()

        cancel_task(notpaid_manager, booking.id)  # Cancel task associated to booking
        cancel_task(events_done_manager, booking.id)  # Cancel task associated to booking

    else:
        return Http404

    return redirect(reverse('trainwell:dashboard'))

@gerent_required
def create_invoice(booking):
    TAX = 0.21
    price = 0

    selections = booking.selection_set.all()

    for s in selections:
        place = Place.objects.get(id=s.place.id)
        price = price + (float(place.price_hour) * ((100 - place.discount)/100))

    price = float(price) * (1 + TAX)
    invoice = Invoice(booking=booking, price=price,
                      concept="Booking: " + booking.name,
                      period_init=selections.first().datetime_init,
                      period_end=selections.first().datetime_init,)

    invoice.save()
    setup_task_invoice(invoice)

    return invoice


class InvoicePdf(View):
    model = Invoice
    template_name = 'trainWellApp/invoice_pdf.html'

    def get(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=self.kwargs.get('pk'))
        selections = invoice.booking.selection_set.all()
        places = {}
        for s in selections:
            value = places.get(s.place.name)
            if value:
                value[1] += 1
            else:
                places[s.place.name] = [s.place.id, 1, s.place.price_hour, s.place.discount,
                                        s.place.price_hour*s.place.discount/100]

        for k, v in places.items(): v += [round(v[1]*v[2], 2), round(v[1]*v[4], 2)]

        return Render.render_pdf(self.template_name, {'invoice': invoice,
                                                      'booking': invoice.booking,
                                                      'places': places,
                                                      'subtotal': round(float(invoice.price)/1.21, 2)})


class Dashboard(ListView):
    model = Booking
    PAGINATE_BY = 20
    template_name = 'trainWellApp/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = self.model.objects.filter(is_deleted=False).filter(planner__user=self.request.user)
        return qs


def isajax_req(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _get_availability(event, week):
    if event is None:
        return json.dumps({}), [], _get_public_days(week)

    # Get event associated places
    all_places = event.places.all()

    weekdays = week.days()
    complete_week = 7 * len(all_places)
    week_avail, open_hours = {}, []

    # Get holidays, booked_dates and open hours for day.
    public_days = _get_public_days(week)
    booked_dates = _get_week_bookings(week)
    ranges = _get_places_ranges(event)
    def_rng = _generate_range()

    # TO-DO incidències
    for d in weekdays:

        curr_rng = def_rng
        for rng in ranges.keys():
            if rng[0] <= d <= rng[1]:
                open_hours.append(tuple(ranges.get(rng)))
                curr_rng = ranges.get(rng).copy()

        # No availability for holidays and weekdays lower today.
        now = datetime.now()
        hour_plus2 = (now + timedelta(hours=2)).replace(minute=00)
        if d in public_days.keys() or d < hour_plus2.date():
            [week_avail.update({d.strftime("%d/%m/%Y") + ',' + f.name: []}) for f in all_places]
            continue

        # Can book from now + 2 hours minimum.
        if d == now.date():
            _tonow = _generate_range(datetime(2020, 1, 1, int(curr_rng.copy().pop(0).split(":")[0]), 00), hour_plus2)
            if _tonow: curr_rng = list(set(curr_rng) - set(_tonow))

        for f in all_places:
            key = d.strftime("%d/%m/%Y") + ',' + f.name + ',' + str(f.id)  # To serialize as JSON
            week_avail[key], booked_hours = curr_rng, []

            for h in curr_rng:
                bdate = booked_dates.get((f, d, h), None)
                if bdate: booked_hours.append(bdate[2].strftime('%H:%M'))

            # Substract booked_hours
            week_avail[key] = list(set(week_avail[key]) - set(booked_hours))

        if len(week_avail) is complete_week: break

    return json.dumps(week_avail), open_hours


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


class BookingScheduleView(ListView):
    model = Selection
    template_name = 'user/userschedule.html'

    def get_queryset(self):
        dailybookings = {}
        day = self.get_day()
        selection = self.model.objects.filter(datetime_init__day=day.day, datetime_init__month=day.month,
                                              datetime_init__year=day.year, booking__is_deleted=False)
        for s in selection:
            if s.booking in dailybookings:
                dailybookings[s.booking].append(s)
            else:
                dailybookings[s.booking] = [s]
        return self.format_data(dailybookings)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        day = self.get_day()

        query = Place.objects.filter(available_from__lt=day, available_until__gt=day)
        if query.exists():
            range_day = query.first()
        else:
            return context

        context.update({'next_day': (day + timedelta(days=1)).strftime("%d/%m/%Y"),
                        'prev_day': (day - timedelta(days=1)).strftime("%d/%m/%Y"),
                        'day': day,
                        'hours': _generate_range(range_day.available_from, range_day.available_until),
                        'isajax': isajax_req(self.request)})

        return context

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
        from collections import OrderedDict

        """ Sort first selections by hours. Then sort by bookings """
        [v.sort(key=lambda x: x.datetime_init) for k, v in bookings.items()]
        bookings = OrderedDict(sorted(bookings.items(), key=lambda x: x[1][0].datetime_init))

        for k, v in bookings.items():
            d = {}
            for e in v: d.setdefault(e.place, []).append(e.datetime_init.strftime("%H:%M"))
            bookings[k] = d
        return bookings

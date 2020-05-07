from datetime import timedelta, datetime, date
import json

from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView
from trainWellApp.decorators import staff_required
from trainWellApp.forms import EventForm, IncidenceForm
from trainWellApp.mixins import StaffRequiredMixin
from trainWellApp.models import Selection, Incidence, Place, Event, Booking, Notification
from trainWellApp.views.trainwell import _generate_range, isajax_req


@staff_required
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


@staff_required
def deleteEvent(request, pk):
    query = Event.objects.filter(pk=pk)

    if query.exists():
        event = query.first()

        if event.is_deleted is True:
            return HttpResponseBadRequest

        event.is_deleted = True
        event.save()

        query = Booking.objects.filter(event=event)

        if query.exists():
            for booking in query:
                description = "Canceled event"
                notification = Notification(booking=booking, name="", description=description)
                notification.save()

                booking.is_deleted = True
                booking.save()

    else:
        return Http404

    return redirect(reverse('staff:dashboard'))


@staff_required
def deletePlace(request, pk):
    query = Place.objects.filter(pk=pk)

    if query.exists():
        place = query.first()

        if place.is_deleted is True:
            return HttpResponseBadRequest

        place.is_deleted = True
        place.save()

        query = Booking.objects.filter(event__places=place)
        if query.exists():
            for booking in query:
                description = "Canceled/Deleted " + place.name
                notification = Notification(booking=booking, name="", description=description)
                notification.save()

                booking.is_deleted = True
                booking.save()

    else:
        return Http404

    return redirect(reverse('staff:dashboard'))


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'staff/add_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'event_form': self.get_form(),
                        'curr_places': self.format_data(),
                        'edit': True})
        return context

    def get_success_url(self):
        # TO-DO: Change reverse url when events_list is defined.
        bookings_id = self.get_form_kwargs()['data']['bookings_affected'].split(',')
        bookings_id = [x for x in bookings_id if x != '']
        description = "Edited event available places"

        if bookings_id:
            for e in bookings_id:
                # Cancel bookings.
                booking = Booking.objects.get(id=int(e))
                booking.is_deleted = True
                booking.save()

                # Create notifications to advertise planners.
                title = "Canceled " + booking.name
                instance = Notification(name=title, description=description, booking=booking)
                instance.save()

        return reverse('staff:booking_list')

    def format_data(self):
        instance = self.get_form_kwargs()['instance']
        return json.dumps([str(p.id) for p in instance.places.all()])


@staff_required
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


class IncidencesListView(StaffRequiredMixin, ListView):
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
@staff_required
def incidence_done(request, pk):
    incidence = Incidence.objects.get(pk=pk)
    incidence.done = True
    incidence.save()

    return redirect(reverse('staff:incidences_list'))


class EventsListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = 'staff/events_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.all().order_by('created')


class PlacesListView(StaffRequiredMixin, ListView):
    model = Place
    template_name = 'staff/places_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.all().order_by('available_until')


# View for head of facilities
class BookingListView(StaffRequiredMixin, ListView):
    model = Selection
    template_name = 'staff/booking_list.html'

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


@staff_required
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
                  str(k.event.name), str(k.phone_number), str(k.name), str(k.id)) for k, v in result.items()]

    return JsonResponse(json.dumps(json_data), safe=False)


@staff_required
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


# TO-DO: Add ManagerRequiredMixin
class NotificationsListView(ListView):
    model = Notification
    template_name = 'manager/notifications_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'read': self.get_queryset1()})
        return context


    def get_queryset(self):
        self.model.objects.filter(is_read=False, is_deleted=False)


    def get_queryset1(self):
        self.model.objects.filter(is_read=True, is_deleted=False)

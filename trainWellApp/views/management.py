from datetime import timedelta, datetime, date
import json

from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, UpdateView
from django.views import View
from rest_framework.views import APIView
from trainWellApp.decorators import staff_required
from trainWellApp.forms import EventForm, IncidenceForm, PlaceForm
from trainWellApp.mixins import StaffRequiredMixin, GerentRequiredMixin
from trainWellApp.models import Selection, Incidence, Place, Event, Booking, Notification
from trainWellApp.views.trainwell import _generate_range, isajax_req


@staff_required
def addEvent(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event_form.save()
            return redirect(reverse('staff:events_list'))

    else:
        event_form = EventForm()

    args = {'event_form': event_form}
    return render(request, 'staff/add_event.html', args)


class EventsListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = 'staff/events_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.filter(is_deleted=False).order_by('created')


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

        return reverse('staff:events_list')

    def format_data(self):
        instance = self.get_form_kwargs()['instance']
        return json.dumps([str(p.id) for p in instance.places.all()])


@staff_required
def deleteEvent(request, pk):
    query = Event.objects.filter(pk=pk)

    if query.exists():
        event = query.first()

        if event.is_deleted is True:
            return HttpResponseBadRequest

        event.places.clear()
        event.is_deleted = True
        event.save()

        query = Booking.objects.filter(event=event)

        if query.exists():
            for booking in query:
                title = "Canceled event"
                description = "Event " + booking.event.name + " was cancelled, and consequently" \
                                                              "your booking " + booking.name
                notification = Notification(booking=booking, name=title, description=description)
                notification.save()

                booking.is_deleted = True
                booking.save()

    else:
        return Http404

    return redirect(reverse('staff:events_list'))


@staff_required
def addPlace(request):
    if request.method == "POST":
        form = PlaceForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('staff:places_list'))

    else:
        form = PlaceForm()

    args = {'form': form}
    return render(request, 'staff/add_places.html', args)


class PlacesListView(StaffRequiredMixin, ListView):
    model = Place
    template_name = 'staff/places_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.filter(is_deleted=False).order_by('available_until')


class PlaceUpdateView(StaffRequiredMixin, UpdateView):
    model = Place
    form_class = PlaceForm
    template_name = 'staff/add_places.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'edit': True})

        return context

    def get_success_url(self):
        return reverse('staff:places_list')


@staff_required
def deletePlace(request, pk):
    query = Place.objects.filter(pk=pk)

    if query.exists():
        place = query.first()

        if place.is_deleted is True:
            return HttpResponseBadRequest()

        place.is_deleted = True
        place.save()

        query = Booking.objects.filter(event__places=place)
        if query.exists():
            for booking in query:
                title = "Canceled/Deleted " + place.name
                description = "Place " + place.name + " was canceled/deleted, and consequently " \
                                                      "your booking " + booking.name
                notification = Notification(booking=booking, name=title, description=description)
                notification.save()

                booking.is_deleted = True
                booking.save()

    else:
        return Http404

    return redirect(reverse('staff:places_list'))


@staff_required
def create_incidence(request):
    form = IncidenceForm()
    if request.method == "POST":
        form = IncidenceForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['limit_date'] >= date.today():
                form.save()

                bookings_id = request.POST['bookings_affected'].split(',')
                bookings_id = [x for x in bookings_id if x != '']
                description = "Incidence affects your booking"

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

                return redirect(reverse('staff:incidences_list'))

    else:
        form = IncidenceForm()

    return render(request, 'staff/add_incidence.html', {'form': form})


class IncidenceUpdateView(StaffRequiredMixin, UpdateView):
    model = Incidence
    form_class = IncidenceForm
    template_name = 'staff/add_incidence.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'IncidenceForm': self.get_form(),
                        'edit': True})
        return context

    def get_success_url(self):
        return reverse('staff:incidences_list')


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


# TO-DO @ajax_required
@staff_required
def incidence_done(request, pk):
    qs = Incidence.objects.filter(pk=pk)

    if qs.exists():
        incidence = qs.first()
        incidence.done = True
        incidence.save()
    else:
        return Http404

    return redirect(reverse('staff:incidences_list'))


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


class NotificationsListView(GerentRequiredMixin, ListView):
    model = Notification
    template_name = 'manager/notifications_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'read': self.get_queryset1()})
        return context

    # TO-DO order query
    def get_queryset(self):
        return self.model.objects.filter(is_read=False, is_deleted=False)

    def get_queryset1(self):
        return self.model.objects.filter(is_read=True, is_deleted=False)


# TO-DO @ajax_required
def notification_read(request, pk):
    qs = Notification.objects.filter(pk=pk)

    if qs.exists():
        notification = qs.first()
        notification.is_read = True
        notification.save()
    else:
        return Http404

    return redirect(reverse('manager:notifications_list'))


class Graphs(View):
    template_name = "manager/graphs.html"

    def get(self, request):
        return render(request, self.template_name, {})


class RendimentGraph(APIView):
    def get(self, request):
        query = Place.objects.all()
        if query.exists() and request.GET['init_data'] and request.GET['end_data']:
            places = {}
            for place in query:
                places[place.name] = self.get_rendiment(place, request.GET['init_data'], request.GET['end_data'])
            return JsonResponse(places)

        else:
            return JsonResponse({"Message": "Error"})

    def get_rendiment(self, place, init_data, end_data):
        init = init_data.split("-")
        end = end_data.split("-")
        d0 = date(int(init[0]), int(init[1]), int(init[2]))
        d1 = date(int(end[0]), int(end[1]), int(end[2]))
        total_hours = (d1 - d0)
        total_hours = total_hours.days * 12

        query = Selection.objects.filter(booking__is_deleted=False).filter(place=place).filter(
            datetime_init__lt=end_data).filter(datetime_init__gt=init_data)

        if query.exists():
            return (query.count() / total_hours) * 100
        else:
            return 0


class UsageGraph(APIView):
    def get(self, request):
        return JsonResponse({"Message": "Done"})
        pass

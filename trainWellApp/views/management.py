import json
from datetime import timedelta, datetime

from django.views.generic import ListView

from trainWellApp.models import Selection, Place
from trainWellApp.views.trainwell import _generate_range, isajax_req


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


from django.shortcuts import render

# Create your views here.
from django.views.generic.detail import DetailView

from trainWellApp.models import Booking


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def bookingcancelation(request, bookingid):
    #Make booking deleted and turn availability on
    booking = Booking.objects.get(id=bookingid)
    booking.is_deleted = True

    return render(request, 'trainWellApp/bookingcancelation.html', )
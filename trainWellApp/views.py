from django.shortcuts import render

# Create your views here.
from django.views.generic.detail import DetailView

from trainWellApp.models import Booking


class BookingDetail(DetailView):
    model = Booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def bookingcancelation(request, bookingpk):
    # Make booking deleted and turn availability on

    booking = Booking.objects.filter(pk=bookingpk, planner__user_id=request.user.id)
    booking.is_deleted = True
    return render(request, 'trainWellApp/dashboard.html', )

from django.urls import path

from trainWellApp.views import *

app_name = "trainWellApp"

urlpatterns = [
    path('bookings/', BookingListView.as_view(), name='booking_list'),
]

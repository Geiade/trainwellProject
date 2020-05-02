from django.urls import path
from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('add_event/', addEvent, name='add_event'),
    path('incidences/', IncidencesListView.as_view(), name='incidences_list'),
    path('incidences/<int:pk>/', incidence_done, name='incidence_done'),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
]

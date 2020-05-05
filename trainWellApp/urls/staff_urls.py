from django.urls import path
from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('', IncidencesListView.as_view(), name="dashboard"),
    path('add_event/', addEvent, name='add_event'),
    path('edit_event/<int:pk>/', EventUpdateView.as_view(), name='edit_event'),
    path('incidences/', IncidencesListView.as_view(), name='incidences_list'),
    path('incidences/<int:pk>/', incidence_done, name='incidence_done'),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('add_incidence/', create_incidence, name='incidence'),
    path('notification/', affected_bookings_asjson, name='notification')
]

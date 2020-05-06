from django.urls import path
from django.views.generic import RedirectView

from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='staff:booking_list'), name="dashboard"),
    path('add_event/', addEvent, name='add_event'),
    path('edit_event/<int:pk>/', EventUpdateView.as_view(), name='edit_event'),
    path('delete_event/<int:pk>/', deleteEvent, name="delete_event"),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('incidences/', IncidencesListView.as_view(), name='incidences_list'),
    path('places/', PlacesListView.as_view(), name='places_list'),
    path('events/', EventsListView.as_view(), name='events_list'),
    path('incidences/<int:pk>/', incidence_done, name='incidence_done'),
    path('add_incidence/', create_incidence, name='incidence'),
    path('notification/', affected_bookings_asjson, name='notification'),
    path('add_place/', addPlace, name="add_place"),
    path('edit_place/', PlaceUpdateView.as_view(), name="edit_place"),
    path('delete_place/<int:pk>/', deletePlace, name="delete_place"),
]

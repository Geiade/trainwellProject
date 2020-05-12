from django.urls import path
from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('notifications/', NotificationsListView.as_view(), name="notifications_list"),
    path('notification/<int:pk>/', notification_read, name='notification_read'),
    path('bookings_state_list/', BookingStateView.as_view(), name='bookings_state_list'),
    path('bookings_state_update/<int:pk>/', BookingStateUpdateView.as_view(), name='bookings_state_update'),

]

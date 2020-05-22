from django.urls import path
from django.views.generic import RedirectView

from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='manager:bookings_state_list'), name="dashboard"),
    path('notifications/', NotificationsListView.as_view(), name="notifications_list"),
    path('notification/<int:pk>/', notification_read, name='notification_read'),
    path('bookings_state_list/', BookingStateView.as_view(), name='bookings_state_list'),
    path('bookings_state_update/<int:pk>/', BookingStateUpdateView.as_view(), name='bookings_state_update'),
    path('graphs/', Graphs.as_view(), name='graphs'),
    path('graphs/api/rendiment', RendimentGraph.as_view(), name='api_rendiment_graph'),
    path('graphs/api/usage', UsageGraph.as_view(), name='api_usage_graph'),
    path('invoices/', InvoiceListView.as_view(), name="invoices_list"),
]

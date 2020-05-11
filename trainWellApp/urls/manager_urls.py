from django.urls import path
from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('notifications/', NotificationsListView.as_view(), name="notifications_list"),
    path('notification/<int:pk>/', notification_read, name='notification_read'),
    path('graphs/', Graphs.as_view(), name='graphs'),
    path('graphs/api/rendiment', RendimentGraph.as_view(), name='api_rendiment_graph'),
    path('graphs/api/usage', UsageGraph.as_view(), name='api_usage_graph'),
]

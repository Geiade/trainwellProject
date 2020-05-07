from django.urls import path
from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('notifications/', NotificationsListView.as_view(), name="notifications_list")
]

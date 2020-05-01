from django.urls import path

from trainWellApp.views.management import *

app_name = "trainWellApp"

urlpatterns = [
    path('add_event/', addEvent, name='add_event'),
]

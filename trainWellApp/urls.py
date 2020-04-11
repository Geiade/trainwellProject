from django.conf.urls import url
from django.urls import path

from trainWellApp import views
from trainWellApp.views import *
from trainWellApp.views import booking_view

"""trainwell URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

app_name = "trainWellApp"

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/<int:pk>/', BookingDetail.as_view(), name='booking-detail'),
    path('booking/<int:pk>/bookingcancelation/', views.bookingcancelation, name='booking_cancelation'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    url(r'^add_booking', booking_view, name='addBooking'),
]

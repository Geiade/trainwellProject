from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Planner(models.Model):
    over_18 = models.BooleanField()
    last_modified = models.DateTimeField()
    created = models.DateTimeField()
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Place(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Booking(models.Model):
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.PROTECT)
    planner = models.ForeignKey(Planner, blank=True, null=True, on_delete=models.PROTECT)
    place = models.ForeignKey(Place, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=10)  # TODO django-phonenumber-field
    datetime_init = models.DateTimeField()
    datetime_end = models.DateTimeField()

    def __str__(self):
        return str(self.event) + " - " + str(self.planner) + " - " + str(self.place) + ": " + str(self.datetime_init)


class Invoice(models.Model):
    booking = models.ForeignKey(Booking, blank=True, null=True, on_delete=models.PROTECT)
    planner = models.ForeignKey(Planner, blank=True, null=True, on_delete=models.PROTECT)  # TODO booking has one alread
    price = models.FloatField()
    concept = models.CharField(max_length=250)
    payment_method = models.CharField(max_length=20)  # TODO create payment_method model
    period_init = models.DateTimeField()
    period_end = models.DateTimeField()

    def __str__(self):
        return str(self.booking) + " - " + str(self.planner) + ":" + str(self.price) + " by " + self.payment_method

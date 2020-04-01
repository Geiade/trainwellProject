from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Planner(models.Model):
    over_18 = models.BooleanField()
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.PROTECT)

    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, related_name="planners", on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return self.user.first_name + " " + self.user.last_name


class Place(models.Model):
    name = models.CharField(max_length=30)
    price_hour = models.DecimalField(max_digits=8, decimal_places=2)
    available_from = models.DateTimeField()
    available_until = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="place_images/", default="place_images/default.png", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=30)
    places = models.ManyToManyField(Place, related_name="events")

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Booking(models.Model):
    event = models.ForeignKey(Event, blank=True, null=True, on_delete=models.PROTECT)
    planner = models.ForeignKey(Planner, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=10)  # TODO django-phonenumber-field
    datetime_init = models.DateTimeField()
    datetime_end = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event) + " - " + str(self.planner) + " - " + str(self.event.places) + ": " + str(
            self.datetime_init)


class Invoice(models.Model):
    booking = models.ForeignKey(Booking, blank=True, null=True, on_delete=models.PROTECT)
    price = models.FloatField()
    concept = models.CharField(max_length=250)
    payment_method = models.CharField(max_length=20)  # TODO create payment_method model
    period_init = models.DateTimeField()
    period_end = models.DateTimeField()
    is_paid = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.booking) + " - " + str(self.booking.planner) + ":" + str(
            self.price) + " by " + self.payment_method

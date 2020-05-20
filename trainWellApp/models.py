from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.

class Planner(models.Model):
    over_18 = models.BooleanField()
    is_staff = models.BooleanField(default=False)
    is_gerent = models.BooleanField(default=False)
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
    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),
                                                                  MaxValueValidator(100)])
    available_from = models.DateTimeField()
    available_until = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="place_images/", default="place_images/default.png", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Map(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to="maps/", default="place_images/default.png", blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=30)
    places = models.ManyToManyField(Place, related_name="events")
    color = models.CharField(max_length=16, default='#cc73e1')

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

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event) + " - " + str(self.name) + " - " + str(self.planner)

    def get_selection(self):
        query = Selection.objects.filter(booking=self)
        if query.exists():
            return query.first()


class Selection(models.Model):
    booking = models.ForeignKey(Booking, blank=True, null=True, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, blank=True, null=True, on_delete=models.CASCADE)
    datetime_init = models.DateTimeField()

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.place.name) + " - " + str(self.datetime_init)


class Invoice(models.Model):
    BOOKING_STATES = ((1, 'Pagada'), (2, 'Impagada'), (3, 'Cancelada pagada'),
                      (4, 'Cancelada impagada'), (5, 'Cancelada fora de termini'))

    PAYMENT_METHODS = ((1, 'Credit card'), (2, 'Cash'), (3, 'Bank Transfer'), (4, 'Bank check'))

    booking = models.OneToOneField(Booking, blank=True, null=True, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    concept = models.CharField(max_length=250)
    payment_method = models.PositiveIntegerField(choices=PAYMENT_METHODS, default=PAYMENT_METHODS[1][0])
    period_init = models.DateTimeField()
    period_end = models.DateTimeField()
    booking_state = models.PositiveIntegerField(choices=BOOKING_STATES, default=BOOKING_STATES[1][0])

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.booking) + " - " + str(self.booking.planner) + ":" + str(self.price)

    def get_payment_method(self):
        return self.PAYMENT_METHODS[self.payment_method - 1][1]

    def get_booking_state(self):
        return self.BOOKING_STATES[self.booking_state - 1][1]

    def get_color(self):
        if self.booking_state == 3 or self.booking_state == 4 or self.booking_state == 5:
            return "#ffff00"
        elif self.booking_state == 2:
            return "#ff0000"
        else:
            return "#33cc33"


class Incidence(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()
    limit_date = models.DateField()
    disabled = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    places = models.ManyToManyField(Place)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) + " - " + str(self.limit_date)


class Notification(models.Model):
    TYPES = ((1, 'USER'), (2, 'ADMIN'))

    booking = models.ForeignKey(Booking, blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    description = models.TextField()
    level = models.PositiveIntegerField(choices=TYPES, default=[1][0])
    is_read = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) + " - " + str(self.description) + " - " + str(self.booking)

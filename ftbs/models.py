from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.


class User(AbstractUser):
    telephone = models.CharField(max_length=20, blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s %s %s %s' % (self.username, self.password, self.email, self.telephone)


class Candidate(models.Model):
    name = models.CharField(max_length=20)
    identity = models.CharField(unique=True, max_length=20)
    gender = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.identity, self.contact, self.gender)


class Airplane(models.Model):
    type = models.CharField(max_length=10, blank=True, null=True)
    duration = models.CharField(max_length=10)
    capacity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s %s %d' % (self.type, self.duration, self.capacity)


class Airline(models.Model):
    name = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=20, blank=True, null=True)
    account = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.name, self.address)


class Flight(models.Model):
    airline = models.ForeignKey(Airline, models.DO_NOTHING)
    plane = models.ForeignKey(Airplane, models.DO_NOTHING, blank=True, null=True)
    code = models.CharField(max_length=10)
    start = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    takeoff_time = models.DateTimeField()
    landing_time = models.DateTimeField()
    flight_price = models.IntegerField()

    def __str__(self):
        return '%s %s %s %s %d ' % (self.start, self.destination, self.takeoff_time, self.landing_time,
                                    self.flight_price)


class Seat(models.Model):
    row = models.IntegerField()
    column = models.CharField(max_length=1)

    def __str__(self):
        return '%d %s' % (self.row, self.column)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)
    passenger = models.ForeignKey(Candidate, models.DO_NOTHING)
    flight = models.ForeignKey(Flight, models.DO_NOTHING)
    seat = models.ForeignKey(Seat, models.DO_NOTHING)
    order_price = models.IntegerField()
    order_state = models.IntegerField()  # 0 not paid, 1 paid, 2 reschedule, 3 be rescheduled, 4 cancel
    order_time = models.DateTimeField()

    def __str__(self):
        return '%d %d %s' % (self.order_price, self.order_state, self.order_time)


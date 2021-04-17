"""Agenda models."""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class ReservationManager(models.Manager):
    """Reservation manager."""

    def format_date(self, date):
        """Format the form input date to fit the requirements"""
        date = date.split('/')
        date = '{}-{}-{}'.format(date[2], date[1], date[0])
        return date

    def randomColor(self):
        """Pick a random color for the calendar events"""
        colors = ['#122f5c', '#102340', '#1f4278', '#184a96', '#1f1354', '#1f0d6e', '#361f9c']
        randint = random.randint(0, 6)
        return colors[randint]

    def create_or_update_reservation(self, form, user, id):
        start_date = self.format_date(form.data['start_date'])
        end_date = self.format_date(form.data['end_date'])
        if id == 0:
            random_color = self.randomColor()
            return Reservation.objects.get_or_create(name=form.data['name'], start_date=start_date, end_date=end_date, description=form.data['description'], color=random_color, user=user)
        else:
            reservation = Reservation.objects.filter(id=id)
            if user == reservation.first().user or user.is_superuser or user.is_staff:
                reservation.update(name=form.data['name'], start_date=start_date, end_date=end_date, description=form.data['description'])
                return reservation


class Reservation(models.Model):
    """Reservation model."""

    name = models.CharField(max_length=200, unique=False, default="Mon nom")
    description = models.TextField(default="Description", blank=True)
    color = models.CharField(max_length=50, unique=False, default="blue")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reservation", default=1)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    objects = ReservationManager()

    def __str__(self):
        """Return the name."""
        return self.name

"""Agenda models."""
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# One colour per member, the same on the calendar and the home page
STAY_COLORS = ['#ae5029', '#3e5540', '#2f5d7c', '#8a5a38', '#7b3f6e',
               '#56704f', '#9d3626', '#5b5a8c', '#7a6a2a', '#35686a']


def stay_color(user_id):
    return STAY_COLORS[(user_id or 0) % len(STAY_COLORS)]


class ReservationQuerySet(models.QuerySet):
    def overlapping(self, stay):
        """Other stays that share a night with `stay`, in date order.

        A departure and an arrival on the same day is a hand-over, not a
        clash. A stay that starts and ends the same day counts as that day.
        """
        candidates = (self.filter(start_date__lte=stay.end_date, end_date__gte=stay.start_date)
                      .exclude(pk=stay.pk).select_related("user").order_by("start_date"))
        start, end = stay.occupied_days()
        return [other for other in candidates
                if other.occupied_days()[0] < end and start < other.occupied_days()[1]]


class Reservation(models.Model):
    """Reservation model."""

    name = models.CharField(max_length=200, unique=False)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=50, unique=False, default="blue")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_reservation", default=1)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)

    objects = ReservationQuerySet.as_manager()

    def __str__(self):
        """Return the name."""
        return self.name

    @property
    def color_for_display(self):
        return stay_color(self.user_id)

    def occupied_days(self):
        """[first day, day after the last night), a one-day visit being one day."""
        return self.start_date, max(self.end_date, self.start_date + timedelta(days=1))

    def can_be_changed_by(self, user):
        return user == self.user or user.is_superuser or user.is_staff

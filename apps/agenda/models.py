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
    # For a stay renewed every year: the start date of the first one, so the
    # renewed dates keep to the same period instead of drifting
    anchor_date = models.DateField("date de référence", null=True, blank=True)

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


class ExchangeQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Exchange.PENDING)

    def involving(self, stay):
        return self.filter(models.Q(offered=stay) | models.Q(requested=stay))


class Exchange(models.Model):
    """A member offers one of their stays for the dates of someone else's."""

    PENDING, ACCEPTED, DECLINED, CANCELLED, OUTDATED = "pending", "accepted", "declined", "cancelled", "outdated"
    STATUSES = [
        (PENDING, "En attente"),
        (ACCEPTED, "Accepté"),
        (DECLINED, "Refusé"),
        (CANCELLED, "Annulé"),
        (OUTDATED, "Plus d'actualité"),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchanges_sent")
    offered = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="+")
    requested = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="+")
    message = models.TextField("message", blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    # The dates as they were when asked: a stay moved since cannot be swapped
    offered_start = models.DateField()
    offered_end = models.DateField()
    requested_start = models.DateField()
    requested_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    objects = ExchangeQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "échange de séjour"
        verbose_name_plural = "échanges de séjours"

    def __str__(self):
        return f"{self.offered} ⇄ {self.requested} ({self.get_status_display()})"

    @property
    def owner(self):
        """Who has to answer."""
        return self.requested.user

    def still_valid(self):
        return ((self.offered.start_date, self.offered.end_date) == (self.offered_start, self.offered_end)
                and (self.requested.start_date, self.requested.end_date) == (self.requested_start, self.requested_end)
                and self.offered.user_id == self.requester_id
                and self.requested.user_id != self.requester_id)

    def swap(self):
        """Each stay takes the other's dates."""
        offered, requested = self.offered, self.requested
        offered.start_date, requested.start_date = self.requested_start, self.offered_start
        offered.end_date, requested.end_date = self.requested_end, self.offered_end
        # A yearly stay's reference date belongs to its period, which moves too
        offered.anchor_date, requested.anchor_date = requested.anchor_date, offered.anchor_date
        fields = ["start_date", "end_date", "anchor_date"]
        offered.save(update_fields=fields)
        requested.save(update_fields=fields)

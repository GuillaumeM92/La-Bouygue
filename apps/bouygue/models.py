from django.conf import settings
from django.db import models
from django.utils import timezone


class AnnouncementQuerySet(models.QuerySet):
    def current(self):
        return self.filter(expires_at__gt=timezone.now())


class Announcement(models.Model):
    """An important message every member sees until it expires."""

    title = models.CharField("titre", max_length=120)
    message = models.TextField("message")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, related_name="announcements")
    created_at = models.DateTimeField("publiée le", auto_now_add=True)
    expires_at = models.DateTimeField("visible jusqu'au")
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                     related_name="announcements_read")

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "annonce"

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        return self.expires_at > timezone.now()

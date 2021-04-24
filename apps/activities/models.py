from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser


class Activity(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Titre"))
    content = models.TextField(verbose_name=_("Description"))
    content2 = models.TextField(verbose_name=_("Précisions"))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    difficulty = models.SmallIntegerField(
        default=0,
        choices=[(0, "Très facile"), (1, "Facile"), (2, "Moyen"),
                 (3, "Difficile"), (4, "Très difficile")],
        verbose_name=_("Difficulté"),
    )
    duration = models.CharField(max_length=20, verbose_name=_("Durée"))
    distance = models.CharField(max_length=20, verbose_name=_("Temps de route"))
    image = models.ImageField(blank=True, upload_to="activities")
    image2 = models.ImageField(blank=True, upload_to="activities")

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ["-date_posted"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.pk})


class ActivityComment(models.Model):
    content = models.TextField(verbose_name=_(''))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to="comments")

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return str(self.author)

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.activity.pk})

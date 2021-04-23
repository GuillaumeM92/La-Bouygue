from django.db import models
from django.urls import reverse
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser
import datetime


class Work(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Titre"))
    content = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(null=True, upload_to="work")
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    categories = models.SmallIntegerField(
        default=0,
        choices=[(0, "Bricolage"), (1, "Jardinage"), (2, "Plomberie"), (3, "Maçonnerie"), (4, "Autre")],
        verbose_name=_("Catégories"),
    )
    state = models.SmallIntegerField(
        default=0,
        choices=[(0, "À faire"), (1, "En cours"), (2, "Terminé")],
        verbose_name=_("État"),
    )
    status = models.SmallIntegerField(
        default=1,
        choices=[(0, "Peut attendre"), (1, "Important"), (2, "Urgent")],
        verbose_name=_("Statut"),
    )
    cost = models.SmallIntegerField(default=0, verbose_name=_("Coût estimé"))

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("work-detail", kwargs={"pk": self.pk})


class WorkComment(models.Model):
    content = models.TextField(verbose_name= _(''))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to="work/comments")

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return str(self.author)

    def get_absolute_url(self):
        return reverse("work-detail", kwargs={"pk": self.work.pk})

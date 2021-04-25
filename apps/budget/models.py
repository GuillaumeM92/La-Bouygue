from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _


class Budget(models.Model):
    date_posted = models.DateTimeField(default=timezone.now)
    total = models.SmallIntegerField(default=0, verbose_name=_("Nouveau Total"))
    description = models.CharField(max_length=64, verbose_name=_('Brève Description'))

    class Meta:
        verbose_name_plural = "Budget"

    def __str__(self):
        return str(self.date_posted.date())


class Funding(models.Model):
    date_posted = models.DateTimeField(default=timezone.now)
    progress = models.SmallIntegerField(default=0, verbose_name=_("Progression"))
    goal = models.SmallIntegerField(default=0, verbose_name=_("Objectif"))

    class Meta:
        verbose_name_plural = "Funding"

    def __str__(self):
        return str(self.date_posted.date())

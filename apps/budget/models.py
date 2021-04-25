from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _


class Budget(models.Model):
    date_posted = models.DateTimeField(default=timezone.now)
    total = models.SmallIntegerField(default=0, verbose_name=_("Nouveau Total"))
    description = models.CharField(max_length=300, verbose_name=_('Brève Description'))

    class Meta:
        verbose_name_plural = "Budget"

    def __str__(self):
        return str(self.date_posted)

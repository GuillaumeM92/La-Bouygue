from django.db import models
from django.urls import reverse
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser

class InfoPost(models.Model):
    title = models.CharField(max_length=100, verbose_name= _('Titre'))
    content = models.TextField(verbose_name= _('Contenu'))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("infopost-detail", kwargs={"pk": self.pk})

from django.db import models
from django.urls import reverse
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser
from PIL import Image
import datetime

class Activity(models.Model):
    title = models.CharField(max_length=100, verbose_name= _('Titre'))
    content = models.TextField(verbose_name= _('Contenu'))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    difficulty = models.SmallIntegerField(default=0, choices=[(0, 'Très facile'), (1, 'Facile'), (2, 'Moyen'), (3, 'Difficile'), (4, 'Très difficile')])
    duration = models.TimeField(default=datetime.time(00, 00))
    distance = models.SmallIntegerField(default=0)
    image = models.ImageField(default="activity_default.jpg", upload_to="activities")

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-date_posted']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super(Activity, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 600 or img.width > 800:
            output_size = (800, 600)
            img.thumbnail(output_size)
            img.save(self.image.path)


class ActivityImage(models.Model):
    image = models.ImageField(default="default.jpg", upload_to="activities")

    def __str__(self):
        return f"{self.activity.title} image"

    def save(self, *args, **kwargs):
        super(Activity, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 600 or img.width > 800:
            output_size = (800, 600)
            img.thumbnail(output_size)
            img.save(self.image.path)

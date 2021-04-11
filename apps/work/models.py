from django.db import models
from django.urls import reverse
from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser
from PIL import Image
import datetime


class Work(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Titre"))
    content = models.TextField(verbose_name=_("Description"))
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

    # def save(self, *args, **kwargs):
    #     super(Work, self).save(*args, **kwargs)

    #     img = Image.open(self.image.path)

    #     if img.height > 600 or img.width > 800:
    #         output_size = (800, 600)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)


# class WorkImage(models.Model):
#     image = models.ImageField(default="default.jpg", upload_to="activities")

#     def __str__(self):
#         return f"{self.activity.title} image"

#     def save(self, *args, **kwargs):
#         super(Work, self).save(*args, **kwargs)

#         img = Image.open(self.image.path)

#         if img.height > 600 or img.width > 800:
#             output_size = (800, 600)
#             img.thumbnail(output_size)
#             img.save(self.image.path)

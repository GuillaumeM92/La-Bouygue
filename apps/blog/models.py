from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from apps.users.models import MyUser


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Titre'))
    content = models.TextField(verbose_name=_('Contenu'))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to="blog")
    image2 = models.ImageField(blank=True, upload_to="blog")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    content = models.TextField(verbose_name=_(''))
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to="comments")

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return str(self.author)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.post.pk})

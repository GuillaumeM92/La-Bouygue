"""Every photo of the site, for the album and the home page slideshow."""
from dataclasses import dataclass
from datetime import datetime

from django.urls import reverse

from apps.activities.models import Activity, ActivityComment
from apps.info.models import InfoComment, InfoPost
from apps.work.models import Work, WorkComment
from .models import AlbumPhoto


@dataclass
class Photo:
    url: str
    date: datetime
    author: object
    caption: str
    link: str = ""


def _photos(queryset, fields, caption, link):
    for item in queryset.select_related("author"):
        for field in fields:
            image = getattr(item, field)
            if image:
                yield Photo(image.url, item.date_posted, item.author, caption(item), link(item))


def all_photos():
    """Newest first."""
    photos = [Photo(p.image.url, p.date_posted, p.author, p.caption)
              for p in AlbumPhoto.objects.select_related("author")]
    photos += _photos(InfoPost.objects.all(), ["image"], lambda i: i.title,
                      lambda i: reverse("infopost-detail", args=[i.pk]))
    photos += _photos(InfoComment.objects.select_related("infopost"), ["image"], lambda c: c.infopost.title,
                      lambda c: reverse("infopost-detail", args=[c.infopost_id]))
    photos += _photos(Activity.objects.all(), ["image", "image2"], lambda a: a.title,
                      lambda a: reverse("activity-detail", args=[a.pk]))
    photos += _photos(ActivityComment.objects.select_related("activity"), ["image"], lambda c: c.activity.title,
                      lambda c: reverse("activity-detail", args=[c.activity_id]))
    photos += _photos(Work.objects.all(), ["image"], lambda w: w.title,
                      lambda w: reverse("work-detail", args=[w.pk]))
    photos += _photos(WorkComment.objects.select_related("work"), ["image"], lambda c: c.work.title,
                      lambda c: reverse("work-detail", args=[c.work_id]))
    return sorted(photos, key=lambda p: p.date, reverse=True)

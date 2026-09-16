"""Remove the Discussions and Budget sections, keeping the discussions' photos.

The two apps are gone from the code, so their tables are read and dropped with
plain SQL. Photos of posts and comments become album photos (the files stay
where they are). The owner chose not to archive the rest: the nightly dumps
are the only copy left.
"""
from datetime import timezone

from django.db import migrations
from django.utils.dateparse import parse_datetime


def _aware(value):
    """SQLite hands back naive UTC datetimes (or text); PostgreSQL aware ones."""
    if isinstance(value, str):
        value = parse_datetime(value)
    if value is not None and value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


BLOG_TABLES = ["blog_comment", "blog_post"]  # comments first: they point to posts
BUDGET_TABLES = ["budget_funding", "budget_budget"]


def keep_photos_and_drop(apps, schema_editor):
    connection = schema_editor.connection
    AlbumPhoto = apps.get_model("bouygue", "AlbumPhoto")
    MyUser = apps.get_model("users", "MyUser")
    ContentType = apps.get_model("contenttypes", "ContentType")
    tables = set(connection.introspection.table_names())
    users = set(MyUser.objects.values_list("id", flat=True))

    photos = []
    with connection.cursor() as cursor:
        if "blog_post" in tables:
            cursor.execute("SELECT id, title, image, image2, date_posted, author_id FROM blog_post")
            titles = {}
            for post_id, title, image, image2, date_posted, author_id in cursor.fetchall():
                titles[post_id] = title
                for name in (image, image2):
                    if name:
                        photos.append(AlbumPhoto(image=name, caption=title[:200], date_posted=_aware(date_posted),
                                                 author_id=author_id if author_id in users else None))
            if "blog_comment" in tables:
                cursor.execute("SELECT image, date_posted, author_id, post_id FROM blog_comment")
                for image, date_posted, author_id, post_id in cursor.fetchall():
                    if image:
                        photos.append(AlbumPhoto(image=image, caption=titles.get(post_id, "")[:200],
                                                 date_posted=_aware(date_posted),
                                                 author_id=author_id if author_id in users else None))
        AlbumPhoto.objects.bulk_create(photos)

        for table in BLOG_TABLES + BUDGET_TABLES:
            if table in tables:
                cursor.execute("DROP TABLE " + schema_editor.quote_name(table))
        cursor.execute("DELETE FROM django_migrations WHERE app IN ('blog', 'budget')")

    # Their permissions go with them; admin history keeps its text
    ContentType.objects.filter(app_label__in=["blog", "budget"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bouygue", "0002_albumphoto"),
        ("users", "0002_remove_myuser_discussions_viewed"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]

    operations = [
        migrations.RunPython(keep_photos_and_drop, migrations.RunPython.noop, atomic=True),
    ]

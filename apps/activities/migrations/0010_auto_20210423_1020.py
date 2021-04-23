# Generated by Django 3.1.6 on 2021-04-23 08:20

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_auto_20210415_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='activity_default.jpg', force_format='JPEG', keep_meta=True, quality=75, size=[1024, 768], upload_to='activities'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='image2',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='activity_default.jpg', force_format='JPEG', keep_meta=True, quality=75, size=[1024, 768], upload_to='activities'),
        ),
    ]

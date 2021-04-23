# Generated by Django 3.1.6 on 2021-04-23 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_auto_20210423_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitycomment',
            name='image',
            field=models.ImageField(null=True, upload_to='activities/comments'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='image',
            field=models.ImageField(default='activity_default.jpg', upload_to='activities'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='image2',
            field=models.ImageField(default='activity_default.jpg', upload_to='activities'),
        ),
    ]

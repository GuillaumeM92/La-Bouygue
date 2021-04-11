# Generated by Django 3.1.6 on 2021-04-11 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='difficulty',
        ),
        migrations.RemoveField(
            model_name='work',
            name='distance',
        ),
        migrations.RemoveField(
            model_name='work',
            name='duration',
        ),
        migrations.AddField(
            model_name='work',
            name='cost',
            field=models.SmallIntegerField(default=0, verbose_name='Coût estimé'),
        ),
        migrations.AddField(
            model_name='work',
            name='state',
            field=models.SmallIntegerField(choices=[(0, 'À faire'), (1, 'En cours'), (2, 'Terminé')], default=0, verbose_name='État'),
        ),
        migrations.AddField(
            model_name='work',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Peut attendre'), (1, 'Important'), (2, 'Urgent')], default=1, verbose_name='Statut'),
        ),
    ]
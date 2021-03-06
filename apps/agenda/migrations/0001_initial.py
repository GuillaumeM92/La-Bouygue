# Generated by Django 3.1.6 on 2021-04-23 15:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Mon nom', max_length=200)),
                ('description', models.TextField(blank=True, default='Description')),
                ('color', models.CharField(default='blue', max_length=50)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]

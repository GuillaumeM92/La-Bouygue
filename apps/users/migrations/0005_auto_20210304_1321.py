# Generated by Django 3.1.6 on 2021-03-04 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210304_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='username',
        ),
        migrations.AddField(
            model_name='myuser',
            name='name',
            field=models.CharField(default='nom', max_length=40, verbose_name='nom'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='surname',
            field=models.CharField(default='prénom', max_length=30, verbose_name='prénom'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='adresse email'),
        ),
    ]

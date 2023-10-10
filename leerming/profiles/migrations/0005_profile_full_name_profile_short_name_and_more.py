# Generated by Django 4.2.6 on 2023-10-10 16:11
from django.db import migrations
from django.db import models

from leerming.profiles.models import TIMEZONES_CHOICES


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0004_profile_timezone"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="full_name",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="full name"
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="short_name",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="short name"
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="timezone",
            field=models.CharField(
                choices=TIMEZONES_CHOICES,
                default="UTC",
                max_length=50,
                verbose_name="Fuseau horaire",
            ),
        ),
    ]

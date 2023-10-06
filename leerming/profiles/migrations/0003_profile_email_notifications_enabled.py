# Generated by Django 4.2.6 on 2023-10-05 16:25
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="email_notifications_enabled",
            field=models.BooleanField(
                default=True, verbose_name="Notifications par email"
            ),
        ),
    ]
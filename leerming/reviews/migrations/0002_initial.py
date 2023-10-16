# Generated by Django 4.2.6 on 2023-10-16 12:39
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_q", "0017_task_cluster_alter"),
        ("flashcards", "0002_initial"),
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedulemanager",
            name="reviewers",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="schedulemanager",
            name="schedule",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="django_q.schedule",
            ),
        ),
        migrations.AddField(
            model_name="review",
            name="flashcards",
            field=models.ManyToManyField(to="flashcards.flashcard"),
        ),
        migrations.AddField(
            model_name="review",
            name="reviewer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="review",
            name="topics",
            field=models.ManyToManyField(to="flashcards.topic"),
        ),
    ]

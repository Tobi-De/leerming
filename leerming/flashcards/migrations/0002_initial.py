# Generated by Django 4.2.6 on 2023-10-16 18:22
import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("flashcards", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="topics",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="flashcard",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flashcards",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="flashcard",
            name="topic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="flashcards",
                to="flashcards.topic",
                verbose_name="Sujet",
            ),
        ),
        migrations.AddConstraint(
            model_name="topic",
            constraint=models.UniqueConstraint(
                fields=("created_by", "title"), name="unique_topic"
            ),
        ),
        migrations.AddConstraint(
            model_name="flashcard",
            constraint=models.UniqueConstraint(
                fields=("owner", "question", "answer"), name="unique_flashcard"
            ),
        ),
    ]

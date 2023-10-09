# Generated by Django 4.2.6 on 2023-10-09 10:32
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("flashcards", "0005_topic_flashcard_topic_topic_unique_topic"),
    ]

    operations = [
        migrations.AlterField(
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
    ]

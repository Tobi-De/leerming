# Generated by Django 4.2.6 on 2023-10-07 12:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flashcards", "0003_remove_flashcard_last_review_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="flashcard",
            name="difficulty",
            field=models.CharField(
                choices=[
                    ("EASY", "Facile"),
                    ("MEDIUM", "Moyen"),
                    ("HARD", "Difficile"),
                ],
                default="HARD",
                max_length=6,
                verbose_name="Difficulté",
            ),
        ),
    ]

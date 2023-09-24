# Generated by Django 4.2.5 on 2023-09-22 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("flashcards", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateField(verbose_name="Date de création")),
                ("score", models.IntegerField(default=0, verbose_name="Score")),
                ("flashcards", models.ManyToManyField(to="flashcards.flashcard")),
            ],
        ),
    ]

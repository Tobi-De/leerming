# Generated by Django 4.2.5 on 2023-09-22 05:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fillinthegapcard",
            name="answer",
            field=models.CharField(max_length=50, verbose_name="Réponse"),
        ),
        migrations.AlterField(
            model_name="fillinthegapcard",
            name="text_with_gap",
            field=models.CharField(max_length=200, verbose_name="Texte à remplir"),
        ),
        migrations.AlterField(
            model_name="frontbackcard",
            name="answer",
            field=models.CharField(max_length=300, verbose_name="Réponse"),
        ),
        migrations.AlterField(
            model_name="frontbackcard",
            name="question",
            field=models.CharField(max_length=250, verbose_name="Question"),
        ),
    ]

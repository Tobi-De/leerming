# Generated by Django 4.2.6 on 2023-10-28 08:20
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0002_alter_uploadeddocument_doc_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadeddocument",
            name="doc_type",
            field=models.CharField(
                choices=[
                    ("PDF_DOC", "Document PDF"),
                    ("DOCX_DOC", "Document Word"),
                    ("HTML_DOC", "Page web"),
                    ("YOUTUBE_VIDEO", "Vidéo Youtube"),
                    ("RAW_TEXT", "Texte brut"),
                ],
                max_length=255,
            ),
        ),
        migrations.AddConstraint(
            model_name="uploadeddocument",
            constraint=models.UniqueConstraint(
                fields=("owner", "title"), name="unique_uploaded_document"
            ),
        ),
    ]
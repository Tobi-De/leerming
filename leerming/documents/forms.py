import tempfile
from pathlib import Path

from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dynamic_forms import DynamicField
from dynamic_forms import DynamicFormMixin
from llama_hub.youtube_transcript.utils import is_youtube_video

from .models import UploadedDocument


def validate_youtube_url(value: str):
    if not is_youtube_video(value):
        raise forms.ValidationError(_("Veuillez saisir une URL youtube valide"))
    return value


youtube_validators = [validate_youtube_url]


class UploadForm(DynamicFormMixin, forms.Form):
    doc_type = forms.ChoiceField(
        label=_("Type de document"),
        choices=UploadedDocument.DocType.choices,
        initial=UploadedDocument.DocType.TEXT_DOC,
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("documents:get_form"),
                "hx-target": "#upload-form",
                "hx-indicator": ".htmx-indicator-upload",
            }
        ),
    )
    title = DynamicField(
        forms.CharField,
        label=_("Titre"),
        required=lambda form: form["doc_type"].value()
        == UploadedDocument.DocType.RAW_TEXT,
        help_text=_(
            "Le titre est obligatoire uniquement si vous voulez entrer un texte brut, "
            "dans la plupart des autres cas nous essayons de déterminer le titre automatiquement"
        ),
    )
    url = DynamicField(
        forms.URLField,
        label=_("URL"),
        include=lambda form: form["doc_type"].value()
        in [UploadedDocument.DocType.WEB_DOC, UploadedDocument.DocType.YOUTUBE_VIDEO],
        validators=lambda form: youtube_validators
        if form["doc_type"].value() == UploadedDocument.DocType.YOUTUBE_VIDEO
        else [],
    )
    # TODO: limit to pdf only
    file = DynamicField(
        forms.FileField,
        label=_("Fichier"),
        include=lambda form: form["doc_type"].value()
        == UploadedDocument.DocType.TEXT_DOC,
    )
    text = DynamicField(
        forms.CharField,
        widget=forms.Textarea(),
        label=_("Texte"),
        include=lambda form: form["doc_type"].value()
        == UploadedDocument.DocType.RAW_TEXT,
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        title = cleaned_data.get("title")
        if in_memory_file := cleaned_data.pop("file", None):
            original_filename = Path(in_memory_file.name)
            with tempfile.NamedTemporaryFile(
                suffix=original_filename.suffix, delete=False
            ) as temp_file:
                for chunk in in_memory_file.chunks():
                    temp_file.write(chunk)
            cleaned_data["temp_file"] = Path(temp_file.name)
            cleaned_data["title"] = title or original_filename.stem
        return cleaned_data

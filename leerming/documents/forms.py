import tempfile
from pathlib import Path

from django import forms
from django.core.validators import FileExtensionValidator
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dynamic_forms import DynamicField
from dynamic_forms import DynamicFormMixin
from llama_hub.youtube_transcript.utils import is_youtube_video

from .models import get_title_from
from .models import UploadedDocument


class UploadForm(DynamicFormMixin, forms.Form):
    doc_type = forms.ChoiceField(
        label=_("Type de document"),
        choices=UploadedDocument.DocType.choices,
        initial=UploadedDocument.DocType.PDF_DOC,
        widget=forms.Select(
            attrs={
                "hx-get": reverse_lazy("documents:get_form"),
                "hx-target": "#upload-form",
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
    )

    pdf_file = DynamicField(
        forms.FileField,
        label=_("Fichier"),
        include=lambda form: form["doc_type"].value()
        == UploadedDocument.DocType.PDF_DOC,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".pdf",
            }
        ),
    )
    docx_file = DynamicField(
        forms.FileField,
        label=_("Fichier"),
        include=lambda form: form["doc_type"].value()
        == UploadedDocument.DocType.DOCX_DOC,
        validators=[FileExtensionValidator(allowed_extensions=["docx"])],
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".docx",
            }
        ),
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
        user = self.context.get("user")
        doc_type = cleaned_data.get("doc_type")
        url = cleaned_data.get("url")

        if (
            url
            and doc_type == UploadedDocument.DocType.YOUTUBE_VIDEO
            and not is_youtube_video(url)
        ):
            raise forms.ValidationError(
                {"url": _("Veuillez saisir une URL youtube valide")}
            )

        in_memory_file = cleaned_data.pop("pdf_file", None) or cleaned_data.pop(
            "docx_file", None
        )

        if in_memory_file:
            title = title or Path(in_memory_file.name).stem

        if doc_type in [
            UploadedDocument.DocType.WEB_DOC,
            UploadedDocument.DocType.YOUTUBE_VIDEO,
        ]:
            title = title or get_title_from(url=cleaned_data.get("url"))

        cleaned_data["title"] = title

        # fixme: checking for title uniqueness, but current implementation does not look good
        if UploadedDocument.objects.filter(title=title, owner_id=user).exists():
            raise forms.ValidationError(
                _(f"Un document avec le title {title} existe déjà")
            )

        if in_memory_file:
            with tempfile.NamedTemporaryFile(
                suffix=Path(in_memory_file.name).suffix, delete=False
            ) as temp_file:
                for chunk in in_memory_file.chunks():
                    temp_file.write(chunk)
            cleaned_data["temp_file"] = Path(temp_file.name)
        return cleaned_data

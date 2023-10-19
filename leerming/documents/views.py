from django.http import HttpRequest
from django.shortcuts import render

from django import forms
from django.template.response import TemplateResponse

from .models import UploadedDocument
from django.utils.translation import gettext_lazy as _

class UploadForm(forms.Form):
    doc_type = forms.ChoiceField(label=_("Type de document"), choices=UploadedDocument.DocType.choices)
    url = forms.URLField(label=_("URL"), required=False)



def upload(request:HttpRequest):
    return TemplateResponse(request, "documents/upload.html", {"form": UploadForm()})

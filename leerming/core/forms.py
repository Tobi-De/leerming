from django import forms
from django.forms.renderers import TemplatesSetting


class FormRenderer(TemplatesSetting):
    form_template_name = "forms/form.html"


def clean_masked_phone(form: forms.Form):
    # a mask is applied on phone in the frontend, so we need to clean before saving to the db
    phone = form.cleaned_data.get("phone", None)
    if phone:
        phone = phone.replace("-", "").replace(" ", "")
    return phone

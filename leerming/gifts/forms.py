from django import forms
from django.utils.translation import gettext_lazy as _

from leerming.users.models import User


def recipient_exists_in_db(email: str):
    try:
        User.objects.get(email=email)
    except User.DoesNotExist as e:
        raise forms.ValidationError(
            _(f"Utilisateur avec le {email} introuvable")
        ) from e


class GiftForm(forms.Form):
    recipient_email = forms.EmailField(label="", validators=[recipient_exists_in_db])

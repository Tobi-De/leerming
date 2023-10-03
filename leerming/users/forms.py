from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import User


class SignupForm(AllauthSignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    """

    full_name = forms.CharField(
        label=_("Nom complet"),
        widget=forms.TextInput(attrs={"placeholder": "Entrez votre nom complet"}),
        required=False,
    )
    short_name = forms.CharField(
        label=_("Nom court"),
        widget=forms.TextInput(
            attrs={"placeholder": "Entrez votre petit nom ou un prénom"}
        ),
        required=False
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            self.add_error("email", _("Un compte existe déjà avec cette adresse email"))
        return email

    def save(self, request: HttpRequest):
        user = super().save(request)
        user.full_name = self.cleaned_data["full_name"]
        user.short_name = self.cleaned_data["short_name"]
        user.save()
        return user

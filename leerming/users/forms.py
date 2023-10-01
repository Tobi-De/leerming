from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.http import HttpRequest


class SignupForm(AllauthSignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    """

    full_name = forms.CharField(
        label="Nom complet",
        widget=forms.TextInput(attrs={"placeholder": "Entrez votre nom complet"}),
        required=False,
    )
    short_name = forms.CharField(
        label="Nom court",
        widget=forms.TextInput(
            attrs={"placeholder": "Entrez votre petit nom ou un prénom"}
        ),
        required=False,
    )

    def save(self, request: HttpRequest):
        user = super().save(request)
        user.full_name = self.cleaned_data["full_name"]
        user.short_name = self.cleaned_data["short_name"]
        user.save()
        return user

from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .forms import ProfileForm
from .models import Profile


def register(request: HttpRequest):
    form = ProfileForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Profile.objects.get_or_create(**form.cleaned_data, user=request.user)
        return redirect("cards:index")
    return TemplateResponse(request, "profiles/register.html", {"form": form})

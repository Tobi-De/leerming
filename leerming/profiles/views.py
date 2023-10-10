from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .decorators import profile_required
from .forms import ProfileEditForm
from .forms import ProfileForm
from .models import Profile


def register(request: HttpRequest):
    form = ProfileForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Profile.objects.get_or_create(user=request.user, defaults=form.cleaned_data)
        return redirect("flashcards:index")
    return TemplateResponse(request, "profiles/register.html", {"form": form})


@profile_required
def edit(request: HttpRequest):
    profile = request.user.profile
    form = ProfileEditForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("profiles:edit")
    return TemplateResponse(request, "profiles/edit.html", {"form": form})

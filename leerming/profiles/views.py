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
    user = request.user
    form = ProfileEditForm(
        request.POST or None,
        initial={
            "review_time": profile.review_time.strftime("%H:%M"),
            "review_days": profile.review_days,
            "short_name": user.short_name,
            "full_name": user.full_name,
        },
    )
    if request.method == "POST" and form.is_valid():
        profile.review_time = form.cleaned_data["review_time"]
        profile.review_days = form.cleaned_data["review_days"]
        profile.save()
        user.short_name = form.cleaned_data["short_name"]
        user.full_name = form.cleaned_data["full_name"]
        user.save()
        return redirect("profiles:edit")
    return TemplateResponse(request, "profiles/edit.html", {"form": form})

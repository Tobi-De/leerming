from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse

from .models import Profile


def profile_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                request.user.profile  # noqa
            except Profile.DoesNotExist:
                return redirect(reverse("profiles:register"))
        return view_func(request, *args, **kwargs)

    return wrapper

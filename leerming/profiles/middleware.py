
from django.shortcuts import redirect
from django.urls import reverse

from .models import Profile


def create_user_profile(get_response):
    def middleware(request):
        on_create_view = request.path == reverse("profiles:create")
        if request.user.is_authenticated and not on_create_view:
            try:
                request.user.profile
            except Profile.DoesNotExist:
                return redirect("profiles:create")
        return get_response(request)

    return middleware


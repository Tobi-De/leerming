from django.shortcuts import redirect
from django.urls import reverse

from .models import Profile


def register_profile_middleware(get_response):
    def middleware(request):
        register_url = reverse("profiles:register")
        on_register_view = request.path == register_url
        if request.user.is_authenticated and not on_register_view:
            try:
                request.user.profile
            except Profile.DoesNotExist:
                return redirect(register_url)
        return get_response(request)

    return middleware

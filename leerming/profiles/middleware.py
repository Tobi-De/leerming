from django.shortcuts import redirect
from django.urls import reverse

from .models import Profile


def check_user_registration(get_response):
    def middleware(request):
        register_url = reverse("profiles:register")
        views_to_exclude = [register_url, reverse("django_browser_reload:events")]
        exempt_from_check = request.path not in views_to_exclude
        if request.user.is_authenticated and exempt_from_check:
            try:
                request.user.profile
            except Profile.DoesNotExist:
                return redirect(register_url)
        return get_response(request)

    return middleware

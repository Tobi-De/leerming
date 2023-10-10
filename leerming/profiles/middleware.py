import zoneinfo

from django.utils import timezone

from .models import Profile


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                timezone.deactivate()
            else:
                timezone.activate(zoneinfo.ZoneInfo(profile.timezone))
        else:
            timezone.deactivate()
        return self.get_response(request)

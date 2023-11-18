from contextlib import suppress

from django.apps import AppConfig
from django.db import IntegrityError


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "leerming.profiles"

    def ready(self):
        from django_q.tasks import schedule
        from django.utils import timezone

        with timezone.override("UTC"):
            tomorrow = timezone.now().replace(hour=1, minute=0)

            with suppress(IntegrityError):
                schedule(
                    "leerming.profiles.tasks.register_users_to_reviews",
                    name="register_users_to_reviews",
                    schedule_type="D",
                    next_run=tomorrow,
                )

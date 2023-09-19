from django.db import models

from model_utils.models import TimeStampedModel
from django_pydantic_field import SchemaField
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE


class Profile(TimeStampedModel, LifecycleModelMixin):
    class Weekday(models.TextChoices):
        MONDAY = "MON", _("Lundi")
        TUESDAY = "TUE", _("Mardi")
        WEDNESDAY = "WED", _("Mercredi")
        THURSDAY = "THU", _("Jeudi")
        FRIDAY = "FRI", _("Vendredi")
        SATURDAY = "SAT", _("Samedi")
        SUNDAY = "SUN", _("Dimanche")

    user = models.OneToOneField(
        "users.User", related_name="profile", on_delete=models.CASCADE
    )
    review_days = SchemaField(list[Weekday])
    review_time = models.TimeField()

    @hook(AFTER_CREATE)
    def create_review_session_scheduler(self):
        # TODO
        pass

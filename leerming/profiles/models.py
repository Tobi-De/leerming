from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE, BEFORE_SAVE
from django_q.models import Schedule
from model_utils.models import TimeStampedModel

from leerming.reviews.models import Review


class Profile(TimeStampedModel, LifecycleModelMixin):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, _("Lundi")
        TUESDAY = 1, _("Mardi")
        WEDNESDAY = 2, _("Mercredi")
        THURSDAY = 3, _("Jeudi")
        FRIDAY = 4, _("Vendredi")
        SATURDAY = 5, _("Samedi")
        SUNDAY = 6, _("Dimanche")

    user = models.OneToOneField(
        "users.User", related_name="profile", on_delete=models.CASCADE
    )
    review_days = ArrayField(models.PositiveSmallIntegerField(choices=Weekday.choices))
    review_time = models.TimeField()

    @cached_property
    def review_scheduler_name(self) -> str:
        return f"{self.user.email}_review_scheduler"

    def is_in_review_days(self, day: Weekday) -> bool:
        return day in self.review_days

    @hook(BEFORE_SAVE)
    def sort_review_days(self):
        self.review_days = sorted(self.review_days)

    @hook(AFTER_CREATE)
    def create_next_review_session_schedule(self):
        next_run = Review.get_next_review_datetime(
            reviewer=self.user,
            last_review=Review.get_last_review_datetime(reviewer=self.user),
        )
        schedule, _ = Schedule.objects.get_or_create(
            name=self.review_scheduler_name,
            func="leerming.reviews.tasks.send_review_notification",
            kwargs={"user_id": self.user.id},
            defaults={"next_run": next_run},
        )

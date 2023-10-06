from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_CREATE
from django_lifecycle import AFTER_UPDATE
from django_lifecycle import BEFORE_SAVE
from django_lifecycle import hook
from django_lifecycle import LifecycleModelMixin
from model_utils.models import TimeStampedModel

from leerming.reviews.models import Review
from leerming.reviews.models import ScheduleManager


class Profile(LifecycleModelMixin, TimeStampedModel):
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
    review_days = ArrayField(
        models.PositiveSmallIntegerField(choices=Weekday.choices),
        verbose_name=_("Jours de révision"),
    )
    review_time = models.TimeField(verbose_name=_("Heure de révision"))
    email_notifications_enabled = models.BooleanField(
        default=True, verbose_name=_("Notifications par email")
    )

    def __str__(self):
        return f"Profile of {self.user}"

    @cached_property
    def review_scheduler_name(self) -> str:
        return f"{self.user.email}_review_scheduler"

    def is_in_review_days(self, day: Weekday) -> bool:
        return day in self.review_days

    @hook(BEFORE_SAVE)
    def sort_review_days(self):
        self.review_days = sorted(self.review_days)

    @hook(
        AFTER_UPDATE,
        when_any=["review_days", "review_time"],
        has_changed=True,
    )
    def update_scheduler(self):
        ScheduleManager.remove(reviewer=self.user)
        self.register_for_next_review()

    @hook(AFTER_CREATE)
    def register_for_next_review(self):
        next_review_datetime = Review.get_next_review_datetime(
            reviewer=self.user,
            last_review_date=Review.get_last_review_date(reviewer=self.user),
        )
        ScheduleManager.add(reviewer=self.user, review_datetime=next_review_datetime)

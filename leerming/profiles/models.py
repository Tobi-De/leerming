import datetime as dt
import zoneinfo

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
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


TIMEZONES_CHOICES = [(tz, tz) for tz in zoneinfo.available_timezones()]


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
    full_name = models.CharField(_("full name"), max_length=200, blank=True)
    short_name = models.CharField(_("short name"), max_length=50, blank=True)
    review_days = ArrayField(
        models.PositiveSmallIntegerField(choices=Weekday.choices),
        verbose_name=_("Jours de révision"),
    )
    review_time = models.TimeField(
        verbose_name=_("Heure de révision"), default="18:00"
    )
    timezone = models.CharField(
        verbose_name=_("Fuseau horaire"),
        max_length=50,
        default="UTC",
        choices=TIMEZONES_CHOICES,
    )
    email_notifications_enabled = models.BooleanField(
        default=True, verbose_name=_("Notifications par email")
    )

    def __str__(self):
        return self.full_name or self.short_name or f"Profile of {self.user}"

    @cached_property
    def review_scheduler_name(self) -> str:
        return f"{self.user.email}_review_scheduler"

    def is_in_review_days(self, day: Weekday) -> bool:
        return day in self.review_days

    def get_next_review_datetime(
        self, from_date: dt.date | None = None, include_from_date: bool = False
    ) -> dt.datetime:
        # prevent the function to return dates in the past
        today = timezone.now().date()
        from_date = max(from_date, today)

        if include_from_date:
            condition_check = (  # noqa E731
                lambda weekday: weekday >= from_date.weekday()
            )
        else:
            condition_check = lambda weekday: weekday > from_date.weekday()  # noqa E731

        next_weekday = next(
            (weekday for weekday in self.review_days if condition_check(weekday)),
            self.review_days[0],
        )

        if include_from_date:
            next_review_date = from_date
        else:
            next_review_date = from_date + dt.timedelta(days=1)

        # loop until we find a day that matches the next_weekday
        while next_review_date.weekday() != next_weekday:
            next_review_date += dt.timedelta(days=1)

        next_run = dt.datetime.combine(next_review_date, self.review_time)
        return timezone.make_aware(next_run, zoneinfo.ZoneInfo(self.timezone))

    @hook(BEFORE_SAVE)
    def sort_review_days(self):
        self.review_days = sorted(self.review_days)

    @hook(
        AFTER_UPDATE,
        when_any=["review_days", "review_time", "timezone"],
        has_changed=True,
    )
    def update_scheduler(self):
        ScheduleManager.remove(reviewer=self.user)
        self.register_for_next_review()

    @hook(AFTER_CREATE)
    def register_for_next_review(self):
        now = timezone.now()
        today = now.date()
        last_review_date = Review.get_last_review_date(reviewer=self.user)
        from_date = last_review_date or today
        next_review_datetime = self.get_next_review_datetime(
            from_date=from_date,
            include_from_date=last_review_date and last_review_date != today,
        )
        ScheduleManager.add(reviewer=self.user, review_datetime=next_review_datetime)

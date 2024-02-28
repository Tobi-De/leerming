import datetime as dt

from django.db import models
from django.utils import timezone
from django_q.models import Schedule
from model_utils.models import TimeStampedModel

from ..utils import notify_reviewers
from leerming.users.models import User


class ScheduleManager(TimeStampedModel):
    """
    The aim of this model is to group users according to their review session schedule.
      If some users have their next session on the same day, at the same time, they will be grouped so that notifications are sent
     to them all at the same time, instead of one schedule per user.
     This is mainly a way of getting around the fact that sendpulse campaigns are limited to one every 15 minutes.
    """

    reviewers = models.ManyToManyField(User)
    schedule = models.OneToOneField(
        "django_q.Schedule", on_delete=models.SET_NULL, null=True
    )
    result_task = models.OneToOneField(
        "django_q.Task", on_delete=models.CASCADE, null=True
    )

    def __str__(self) -> str:
        if self.schedule:
            return f"will run at {self.schedule.next_run}"
        return f"ran at {self.result_task.started}"

    @classmethod
    def add(cls, reviewer: User, review_datetime: dt.datetime) -> None:
        try:
            manager = cls.objects.get(schedule__next_run=review_datetime)
        except cls.DoesNotExist:
            manager = cls.objects.create()
            schedule = Schedule.objects.create(
                func="leerming.reviews.tasks.run_schedule_manager",
                next_run=review_datetime,
                kwargs={"manager_id": manager.id},
                hook="leerming.reviews.tasks.update_manager_result_task",
            )
            manager.schedule = schedule
            manager.save()

        manager.reviewers.add(reviewer)
        manager.refresh_from_db()

    @classmethod
    def remove(cls, reviewer: User) -> None:
        for manager in cls.objects.filter(reviewers__in=[reviewer]):
            manager.reviewers.remove(reviewer)
            if not manager.reviewers.exists():
                if manager.schedule:
                    manager.schedule.delete()
                manager.delete()

    def notify_reviewers(self):
        from leerming.reviews.models import Review

        date = timezone.now().date()

        reviewers_to_notify = []
        for reviewer in self.reviewers.select_related("profile").filter(email_notifications_enabled=True):
            last_review_was_today = (
                Review.get_last_review_date(reviewer=reviewer) == date
            )
            on_going_review = bool(Review.get_current_review(reviewer=reviewer))
            if last_review_was_today or on_going_review:
                continue
            reviewers_to_notify.append(reviewer)

        notify_reviewers(reviewers_to_notify)

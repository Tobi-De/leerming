from django.db import models
import datetime as dt
from model_utils.models import TimeStampedModel
from django_pydantic_field import SchemaField
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin, hook, AFTER_CREATE, BEFORE_SAVE
from django_q.models import Schedule
from django.utils.functional import cached_property
from django.utils import timezone


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
    review_days = SchemaField(list[Weekday])
    review_time = models.TimeField()


    @cached_property
    def review_scheduler_name(self)->str:
        return f"{self.user.id}_{self.user}_review_scheduler"

    
    def get_next_review_datetime(self)->dt.datetime:
        today = dt.date.today()
        today_weekday = today.weekday()
        next_weekday = self.review_days[0]
        for weekday in self.review_days:
            if weekday > today_weekday:
                next_weekday = weekday
                break

        next_run_date = today
        while True:
            next_run_date += dt.timedelta(days=1)
            if next_run_date.weekday() == next_weekday:
                break
        
        next_run =  dt.datetime.combine(next_run_date, self.review_time)
        return timezone.get_current_timezone().localize(next_run)

    @hook(BEFORE_SAVE)
    def sort_review_days(self):
        self.review_days = sorted(self.review_days)


    @hook(AFTER_CREATE)
    def create_review_session_scheduler(self):
        # write a the code that create the next review date based on the review_days and review_time
        # get the next day if it code is included in the review_days and for that date get the review_time

        next_run = self.get_next_review_datetime()
        schedule, _ = Schedule.objects.get_or_create(name=self.review_scheduler_name, 
                                                     func="leerming.reviews.tasks.send_review_notification", 
                                                     kwargs={"user_id": self.user.id},
                                                     defaults={"next_run": next_run}
                                                     )
        
        
        

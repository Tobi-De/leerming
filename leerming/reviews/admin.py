from django.contrib import admin

from .models import Review
from .models import ScheduleManager


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reviewer",
        "score_percentage",
        "creation_date",
        "completed_at",
        "created",
        "modified",
    )
    list_filter = (
        "created",
        "modified",
        "reviewer",
        "creation_date",
        "completed_at",
    )
    raw_id_fields = ("flashcards", "topics")


@admin.register(ScheduleManager)
class ScheduleManagerAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "modified", "schedule", "result_task")
    list_filter = ("created", "modified", "schedule", "result_task")

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "short_name",
        "review_days",
        "review_time",
        "created",
        "modified",
        "timezone",
        "email_notifications_enabled",
    )
    list_filter = (
        "created",
        "modified",
        "user",
        "email_notifications_enabled",
    )

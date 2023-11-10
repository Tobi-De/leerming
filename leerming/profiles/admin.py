from django.contrib import admin

from .models import Profile


@admin.action(description="Register selected profiles for next review")
def register_for_next_review(modeladmin, request, queryset):
    for profile in queryset:
        profile.register_for_next_review()


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
    actions = [register_for_next_review]

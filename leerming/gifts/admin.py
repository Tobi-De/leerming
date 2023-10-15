from django.contrib import admin

from .models import Gift


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender",
        "recipient",
        "flashcards",
        "opened_at",
        "created",
        "modified",
    )
    list_filter = (
        "sender",
        "recipient",
        "opened_at",
        "created",
        "modified",
    )

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from .models import FlashCard
from .models import Topic
from .resources import FlashCardResource


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass


@admin.register(FlashCard)
class FlashCardAdmin(ImportExportModelAdmin):
    resource_classes = [FlashCardResource]
    list_display = (
        "id",
        "owner_link",
        "card_type",
        "question",
        "level",
        "next_review_date",
        "mastered_at",
        "created",
    )
    list_filter = (
        "created",
        "modified",
        "owner",
        "next_review_date",
        "mastered_at",
    )

    @admin.display(description="Link to owner of the flashcard")
    def owner_link(self, obj: FlashCard) -> str:
        return mark_safe(  # noqa
            f'<a href="{reverse("admin:users_user_change", args=(obj.owner.id,))}">{obj.owner}</a>'
        )

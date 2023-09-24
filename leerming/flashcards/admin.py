from django.contrib import admin

from .models import FlashCard


@admin.register(FlashCard)
class FlashCardAdmin(admin.ModelAdmin):
    pass

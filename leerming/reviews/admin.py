from django.contrib import admin

from .models import Review, ScheduleManager


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass

@admin.register(ScheduleManager)
class ScheduleManagerAdmin(admin.ModelAdmin):
    pass
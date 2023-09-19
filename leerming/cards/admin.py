from django.contrib import admin

from .models import FillInTheGapCard, FrontBackCard


@admin.register(FrontBackCard)
class FrontBackCardAdmin(admin.ModelAdmin):
    pass


@admin.register(FillInTheGapCard)
class FillInTheGapCardAdmin(admin.ModelAdmin):
    pass

import datetime as dt

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from leerming.flashcards.models import FlashCard
from leerming.users.models import User


class Review(models.Model):
    flashcards = models.ManyToManyField(FlashCard)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    creation_date = models.DateField(verbose_name=_("Date de création"))
    score = models.IntegerField(default=0, verbose_name=_("Score"))

    def increment_score(self):
        self.score += 1
        self.save()

    @cached_property
    def score_percentage(self) -> int:
        total_cards = self.flashcards.count()
        return 0 if total_cards == 0 else round((self.score / total_cards) * 100)

    @classmethod
    def create(cls, for_date: dt.date, user: User) -> "Review":
        return cls(
            flashcards=FlashCard.objects.filter(
                mastered_date__isnull=True,
                last_review_date__lt=for_date
                - dt.timedelta(days=7 ** models.F("level")),
            ),
            user=user,
            creation_date=for_date,
        )

from django.db import models
import datetime as dt
from django.utils.functional import cached_property

from leerming.cards.models import FillInTheGapCard, FrontBackCard


class Review(models.Model):
    fill_in_cards = models.ManyToManyField(FillInTheGapCard)
    front_back_cards = models.ManyToManyField(FrontBackCard)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    creation_date = models.DateField()
    score = models.IntegerField(default=0)

    def increment_score(self):
        self.score += 1
        self.save()

    @cached_property
    def score_percentage(self) -> int:
        total_cards = self.fill_in_cards.count() + self.front_back_cards.count()
        if total_cards == 0:
            return 0
        return round((self.score / total_cards) * 100)

    @classmethod
    def create(cls, for_date: dt.date) -> "Review":
        filter = models.Q(
            mastered_date__isnull=True,
            last_reviewed_date__lt=for_date - dt.timedelta(days=7 ** models.F("level")),
        )

        return cls(
            fill_in_cards=FillInTheGapCard.objects.filter(filter),
            front_back_cards=FrontBackCard.objects.filter(filter),
            creation_date=for_date,
        )

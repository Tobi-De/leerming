from django.db import models

from model_utils.models import TimeStampedModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class BaseCard(TimeStampedModel):
    level = models.IntegerField(
        verbose_name="Niveau",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    last_reviewed_date = models.DateField(
        verbose_name="Date de dernière révision", blank=True, null=True
    )
    mastered_date = models.DateField(
        verbose_name="Date de maîtrise", blank=True, null=True
    )

    class Meta:
        abstract = True

    def review(self, correct_answer: bool):
        if self.mastered_date:
            return
        if correct_answer:
            if self.level < 7:
                self.level += 1
            else:
                self.mastered_date = timezone.now().date()
        else:
            self.level = 1
        self.last_review_date = timezone.now().date()
        self.save()


class FillInTheGapCard(BaseCard):
    text_with_gap = models.TextField(verbose_name="Texte à remplir")
    answer = models.TextField(verbose_name="Réponse", max_length=100)


class FrontBackCard(BaseCard):
    question = models.TextField(verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")

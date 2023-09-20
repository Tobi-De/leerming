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


# The size limits one these fields is to avoid users wasting to much time on creating cards or
# cards too big that they are not really practical.
class FillInTheGapCard(BaseCard):
    text_with_gap = models.CharField(verbose_name="Texte à remplir", max_length=200)
    answer = models.CharField(verbose_name="Réponse", max_length=50)

    @property
    def text_with_gap_soft_size_limit(self):
        return 150

    @property
    def answer_soft_size_limit(self):
        return 30


class FrontBackCard(BaseCard):
    question = models.CharField(verbose_name="Question", max_length=250)
    answer = models.CharField(verbose_name="Réponse", max_length=300)

    @property
    def question_soft_size_limit(self):
        return 150

    @property
    def answer_soft_size_limit(self):
        return 200

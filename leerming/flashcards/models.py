from typing import TypedDict

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class SoftLimit(TypedDict):
    question: int
    answer: int


class FlashCard(TimeStampedModel):
    # TODO probably change the primary key of this to uuid
    class CardType(models.TextChoices):
        FRONT_BACK = "FRONT_BACK", _("Deux faces")
        FILL_IN_THE_GAP = "FILL_IN_THE_GAP", _("Remplissage")

    # The size limits one these fields is to avoid users wasting to much time on
    # creating flashcards or flashcards too big that they are not really practical
    CARD_TYPES_SOFT_LIMITS: dict[CardType, SoftLimit] = {
        CardType.FILL_IN_THE_GAP: {"question": 200, "answer": 50},
        CardType.FRONT_BACK: {"question": 150, "answer": 200},
    }

    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="flashcards"
    )
    card_type = models.CharField(
        verbose_name=_("Type de carte"),
        choices=CardType.choices,
        max_length=20,
        default=CardType.FILL_IN_THE_GAP,
    )
    level = models.IntegerField(
        verbose_name=_("Niveau"),
        default=1,
        help_text=_(
            "Indique la difficulté de la carte, de 1 à 7, 7 étant la plus difficile"
        ),
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    last_review_date = models.DateField(
        verbose_name=_("Date de dernière révision"), blank=True, null=True
    )
    mastered_at = models.DateTimeField(
        verbose_name=_("Maîtrisée à"), blank=True, null=True
    )
    question = models.CharField(
        verbose_name=_("Question / Texte à remplir"), max_length=250
    )
    answer = models.CharField(verbose_name=_("Réponse"), max_length=200)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        if self.card_type == self.CardType.FRONT_BACK:
            return self.question
        return self.question.replace(self.answer, "...")

    @property
    def answer_display(self) -> str:
        if self.card_type == self.CardType.FRONT_BACK:
            return self.answer
        return self.question

    def review(self, correct_answer: bool) -> None:
        if self.mastered_at:
            return
        if correct_answer and self.level < 7:
            self.level += 1
        elif not correct_answer:
            self.level = 1
        if correct_answer and self.level == 7:
            self.mastered_at = timezone.now()
        self.last_review_date = timezone.now().date()
        self.save()

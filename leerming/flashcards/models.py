import datetime as dt

from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Topic(TimeStampedModel):
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="topics"
    )
    title = models.CharField(
        verbose_name=_("Titre"),
        max_length=255,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["created_by", "title"],
                name="unique_topic",
            )
        ]

    def __str__(self) -> str:
        return self.title


class FlashCard(TimeStampedModel):
    LEVEL_TO_DAYS_MAP = {
        1: 1,
        2: 2,
        3: 4,
        4: 7,
        5: 15,
        6: 30,
        7: 60,
    }

    DIFFICULTY_TO_LEVEL_MAP = {
        "EASY": (5, 6, 7),
        "MEDIUM": (3, 4),
        "HARD": (1, 2),
    }

    class Difficulty(models.TextChoices):
        EASY = "EASY", _("Facile")
        MEDIUM = "MEDIUM", _("Moyen")
        HARD = "HARD", _("Difficile")

    class CardType(models.TextChoices):
        FRONT_BACK = "FRONT_BACK", _("Recto / Verso")
        FILL_IN_THE_GAP = "FILL_IN_THE_GAP", _("Remplissage")

    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="flashcards"
    )
    topic = models.ForeignKey(
        Topic,
        verbose_name=_("Sujet"),
        on_delete=models.CASCADE,
        related_name="flashcards",
        blank=True,
        null=True,
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
            "Indique la difficulté de la carte, de 1 à 7 (le niveau le plus difficile)."
        ),
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    # this is a user friendly version of the level
    difficulty = models.CharField(
        verbose_name=_("Difficulté"),
        choices=Difficulty.choices,
        max_length=6,
        default=Difficulty.HARD,
    )
    mastered_at = models.DateTimeField(
        verbose_name=_("Maîtrisée à"), blank=True, null=True
    )
    question = models.CharField(
        verbose_name=_("Question / Texte à remplir"), max_length=250
    )
    answer = models.CharField(verbose_name=_("Réponse"), max_length=200)
    next_review_date = models.DateField(
        verbose_name=_("Date de la prochaine révision"), blank=True, null=True
    )

    def __str__(self):
        if self.card_type == self.CardType.FRONT_BACK:
            return self.question
        return self.question.replace(self.answer, "[...]")

    @property
    def answer_display(self) -> str:
        if self.card_type == self.CardType.FRONT_BACK:
            return self.answer
        return self.question

    def update_level_from_difficulty(self) -> None:
        # when user manually change the difficulty
        self.level = self.DIFFICULTY_TO_LEVEL_MAP.get(self.difficulty)[0]
        review_interval = dt.timedelta(days=self.LEVEL_TO_DAYS_MAP[self.level])
        # would be even better if the from_date was the user last_review date
        self.next_review_date = self.owner.profile.get_next_review_datetime(
            from_date=timezone.now().date() + review_interval, include_from_date=True
        )
        self.save()

    def review(self, correct_answer: bool, for_date: dt.date) -> None:
        if self.mastered_at:
            return
        if correct_answer and self.level < 7:
            self.level += 1
        elif correct_answer and self.level == 7:
            self.mastered_at = for_date
            self.next_review_date = None
            self.save()
            return
        else:
            self.level = 1
        review_interval = dt.timedelta(days=self.LEVEL_TO_DAYS_MAP[self.level])
        self.difficulty = FlashCard.get_difficulty_for(self.level)
        self.next_review_date = self.owner.profile.get_next_review_datetime(
            from_date=for_date + review_interval, include_from_date=True
        )
        self.save()

    @staticmethod
    def get_difficulty_for(level) -> str:
        for key, value in FlashCard.DIFFICULTY_TO_LEVEL_MAP.items():
            if level in value:
                return key

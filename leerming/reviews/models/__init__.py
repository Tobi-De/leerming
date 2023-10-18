from __future__ import annotations

import datetime as dt
import random
from contextlib import suppress
from dataclasses import asdict
from dataclasses import dataclass

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from .schedule import ScheduleManager  # noqa
from leerming.flashcards.models import FlashCard
from leerming.flashcards.models import Topic
from leerming.users.models import User


class ReviewError(Exception):
    pass


class NoCardsToReviewError(ReviewError):
    pass


class SessionEndedError(ReviewError):
    pass


@dataclass
class SessionStore:
    reviewer_email: str
    current_review_id: int
    flashcard_ids: list[int]
    current_card_id: int
    answers: dict[int, bool]

    @staticmethod
    def get_key(reviewer_email: str) -> str:
        return f"review_for_{reviewer_email}"

    @classmethod
    def get(cls, reviewer_email: str) -> SessionStore | None:
        if data := cache.get(cls.get_key(reviewer_email)):
            return cls(**data)

    def save(self) -> None:
        cache.set(self.get_key(self.reviewer_email), asdict(self), timeout=None)

    def delete(self) -> None:
        cache.delete(self.get_key(self.reviewer_email))


class Review(TimeStampedModel):
    """Reviews are made daily, there is only one review per day per user. This constraints
    are made for the sake of simplicity and to help the user being consistent in his learning.
    """

    flashcards = models.ManyToManyField(FlashCard)
    topics = models.ManyToManyField(Topic)
    reviewer = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="reviews"
    )
    score_percentage = models.IntegerField(default=0, verbose_name=_("Score %"))
    creation_date = models.DateField(
        verbose_name=_("Créé le"), editable=False, default=dt.date.today
    )
    completed_at = models.DateTimeField(
        verbose_name=_("Terminé le"), null=True, blank=True
    )

    class Meta:
        ordering = ("-creation_date",)

    def __str__(self):
        return f"Revu du {self.creation_date} - score: {self.score_percentage}%"

    def start(self) -> None:
        flashcards = list(self.flashcards.values_list("id", flat=True))
        random.shuffle(flashcards)
        SessionStore(
            reviewer_email=self.reviewer.email,
            flashcard_ids=flashcards,
            current_card_id=flashcards[0],
            current_review_id=self.id,
            answers={},
        ).save()

    def end(self) -> None:
        session = SessionStore.get(self.reviewer.email)
        answers = session.answers
        completion_date = timezone.now()

        nbr_of_correct_answers = 0
        for flashcard_id, correct_answer in answers.items():
            try:
                self.flashcards.get(id=flashcard_id).review(
                    correct_answer=correct_answer, for_date=completion_date.date()
                )
            except FlashCard.DoesNotExist:
                continue
            if correct_answer:
                nbr_of_correct_answers += 1

        self.score_percentage = self.compute_score_percentage(
            score=nbr_of_correct_answers,
            nbr_of_cards=self.flashcards.count(),
        )

        self.completed_at = completion_date
        self.save()

        # clean session
        session.delete()

        # create reminder for next review
        self.reviewer.profile.register_for_next_review()

    def move_to_next_card(self) -> FlashCard:
        session = SessionStore.get(self.reviewer.email)
        try:
            current_card_index = session.flashcard_ids.index(session.current_card_id)
            next_flashcard_id = session.flashcard_ids[current_card_index + 1]
        except IndexError as e:
            raise SessionEndedError() from e

        session.current_card_id = next_flashcard_id
        session.save()

        try:
            return FlashCard.objects.get(pk=next_flashcard_id)
        except FlashCard.DoesNotExist:
            return self.move_to_next_card()

    def add_answer(self, card_id: int, answer: bool) -> None:
        session = SessionStore.get(self.reviewer.email)
        session.answers[card_id] = answer
        session.save()

    def get_current_card(self) -> tuple[FlashCard, str]:
        session = SessionStore.get(reviewer_email=self.reviewer.email)
        current_card_index = session.flashcard_ids.index(session.current_card_id)
        nbr_of_cards = len(session.flashcard_ids)
        step = f"{current_card_index + 1}/{nbr_of_cards}"
        return FlashCard.objects.get(pk=session.current_card_id), step

    @classmethod
    def get_current_review(cls, reviewer: User) -> Review | None:
        session = SessionStore.get(reviewer_email=reviewer.email)
        if session:
            return cls.objects.filter(pk=session.current_review_id).first()

    @classmethod
    def get_last_review_date(cls, reviewer: User) -> dt.date | None:
        with suppress(AttributeError):
            return (
                cls.objects.filter(reviewer=reviewer, completed_at__isnull=False)
                .order_by("-creation_date")
                .first()
                .creation_date
            )

    @classmethod
    def get_review_start_message(
        cls,
        reviewer: User,
        current_review: Review | None = None,
    ) -> str | None:
        now = timezone.now()
        if not reviewer.profile.is_in_review_days(dt.date.today().weekday()):
            return
        if reviewer.reviews.filter(
            creation_date=now.date(), completed_at__isnull=False
        ).exists():
            return
        if reviewer.reviews.count() == 0:
            return _("Démarrez votre première révision!")
        if current_review:
            return _("Continuez votre révision!")
        reviewer_time = reviewer.profile.review_time
        review_date = now.replace(hour=reviewer_time.hour, minute=reviewer_time.minute)
        # the user can start the review in a two hours range before the review time
        two_hours_before_review_time = review_date - dt.timedelta(hours=2)
        if now > two_hours_before_review_time:
            return _("Démarrer votre révision d'aujourd'hui")

    @classmethod
    def compute_score_percentage(cls, score: int, nbr_of_cards: int) -> int:
        return 0 if nbr_of_cards == 0 else round((score / nbr_of_cards) * 100)

    @classmethod
    def get_flashcards_to_review_for(
        cls, reviewer: User, date: dt.date
    ) -> QuerySet[FlashCard]:
        return reviewer.flashcards.filter(
            models.Q(next_review_date__lte=date)
            | models.Q(next_review_date__isnull=True),
            mastered_at__isnull=True,
        )

    @classmethod
    def get_or_create(
        cls,
        reviewer: User,
        creation_date: dt.date,
        flashcards=QuerySet[FlashCard],
        topics: QuerySet[Topic] | None = None,
    ) -> Review:
        with suppress(ObjectDoesNotExist):
            return cls.objects.get(reviewer=reviewer, creation_date=creation_date)

        instance = cls.objects.create(reviewer=reviewer, creation_date=creation_date)
        instance.flashcards.set(flashcards)
        instance.topics.set(topics)
        return instance

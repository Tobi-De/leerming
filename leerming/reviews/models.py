from __future__ import annotations

import datetime as dt
import random
from contextlib import suppress

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from leerming.flashcards.models import FlashCard
from leerming.users.models import User

review_id_session_key = "review_id"
cards_session_key = "review_cards"
current_card_session_key = "review_current_card"
answers_session_key = "review_scores"


class ReviewError(Exception):
    pass


class NoCardsToReviewError(ReviewError):
    pass


class SessionEndedError(ReviewError):
    pass


class Review(models.Model):
    """Reviews are made daily, there is only one review per day per user. This constraints
    are made for the sake of simplicity and to help the user being consistent in his learning.
    """

    flashcards = models.ManyToManyField(FlashCard)
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

    @classmethod
    def compute_score_percentage(cls, score: int, nbr_of_cards: int) -> int:
        return 0 if nbr_of_cards == 0 else round((score / nbr_of_cards) * 100)

    @classmethod
    def _get_or_create(cls, reviewer: User) -> "Review":
        if not reviewer.flashcards.filter(mastered_at__isnull=True).filter():
            raise NoCardsToReviewError("No cards to review")

        today = dt.date.today()
        instance, created = cls.objects.get_or_create(
            reviewer=reviewer, creation_date=today
        )
        if not created:
            return instance

        cards = []
        for card in reviewer.flashcards.filter(mastered_at__isnull=True):
            if not card.last_review_date:
                cards.append(card)
            elif card.last_review_date < today - dt.timedelta(days=7**card.level):
                cards.append(card)
        if not cards:
            raise NoCardsToReviewError("No cards to review")
        instance.flashcards.add(*cards)
        return instance

    @classmethod
    def start(cls, reviewer: User, request: HttpRequest) -> "Review":
        review = cls._get_or_create(reviewer)

        # if the review is already in the user session then there is nothing to do
        if request.session.get(review_id_session_key):
            # already started
            return review

        cards = review.flashcards.values_list("id", flat=True)
        random.shuffle(cards)
        request.session[review_id_session_key] = review.id
        request.session[cards_session_key] = list(cards)
        request.session[current_card_session_key] = cards[0]
        request.session[answers_session_key] = {}
        return review

    @classmethod
    def end(cls, request: HttpRequest) -> "Review":
        current_review_id = request.session.get(review_id_session_key)
        current_review = cls.objects.get(pk=current_review_id)
        if current_review.completed_at:
            # the review has already been end, nothing to do
            return current_review

        answers = request.session.get(answers_session_key)

        for card_id, correct_answer in answers.items():
            current_review.flashcards.get(id=card_id).review(
                correct_answer=correct_answer
            )

        current_review.score_percentage = cls.compute_score_percentage(
            score=len(
                [
                    correct_answer
                    for _, correct_answer in answers.items()
                    if correct_answer
                ]
            ),
            nbr_of_cards=current_review.flashcards.count(),
        )

        current_review.completed_at = timezone.now()
        current_review.save()

        # clean session
        request.session.pop(current_card_session_key)
        request.session.pop(cards_session_key)
        request.session.pop(review_id_session_key)
        request.session.pop(answers_session_key)

        # create reminder for next review
        current_review.reviewer.profile.create_next_review_session_schedule()
        return current_review

    @classmethod
    def move_to_next_card(cls, request: HttpRequest) -> FlashCard:
        cards = request.session.get(cards_session_key)
        current_card = request.session.get(current_card_session_key)

        try:
            next_card = cards[cards.index(current_card) + 1]
        except IndexError as e:
            raise SessionEndedError() from e

        request.session[current_card_session_key] = next_card

        try:
            return FlashCard.objects.get(pk=next_card)
        except FlashCard.DoesNotExist:
            return cls.move_to_next_card(request)

    @classmethod
    def add_answer(cls, card_id: int, answer: bool, request: HttpRequest) -> None:
        answers = request.session.get(answers_session_key)
        answers[card_id] = answer
        request.session[answers_session_key] = answers

    @classmethod
    def get_current_card(cls, request: HttpRequest) -> FlashCard:
        current_card_id = request.session.get(current_card_session_key)
        return FlashCard.objects.get(pk=current_card_id)

    @classmethod
    def get_current_review(
        cls, reviewer: User, request: HttpRequest | None = None
    ) -> Review | None:
        try:
            if current_review_id := request.session.get(review_id_session_key):
                return cls.objects.get(pk=current_review_id)
        except ObjectDoesNotExist:
            request.session.pop(current_card_session_key)
            request.session.pop(cards_session_key)
            request.session.pop(review_id_session_key)
            request.session.pop(answers_session_key)
        with suppress(ObjectDoesNotExist):
            return cls.objects.get(reviewer=reviewer, completed_at__isnull=True)

    @classmethod
    def get_last_review_datetime(cls, reviewer: User) -> dt.datetime | None:
        with suppress(AttributeError):
            return (
                cls.objects.filter(reviewer=reviewer, completed_at__isnull=False)
                .order_by("-creation_date")
                .first()
                .creation_date
            )

    @classmethod
    def get_last_review(cls, reviewer: User) -> Review:
        return cls.objects.get(reviewer=reviewer, completed_at__isnull=False)

    @classmethod
    def get_next_review_datetime(
        cls, reviewer: User, last_review: dt.datetime | None = None
    ) -> dt.datetime:
        review_days = reviewer.profile.review_days
        review_time = reviewer.profile.review_time

        today = dt.date.today()
        today_weekday = today.weekday()
        next_weekday = next(
            (weekday for weekday in review_days if weekday > today_weekday),
            review_days[0],
        )

        # if the user already a review for today, use tomorrow as the starting point
        if last_review and last_review.date() == today:
            next_review_date = last_review + dt.timedelta(days=1)
        else:
            next_review_date = today

        # loop until we find a day that matches the next_weekday
        while next_review_date.weekday() != next_weekday:
            next_review_date += dt.timedelta(days=1)

        next_run = dt.datetime.combine(next_review_date, review_time)
        return timezone.get_current_timezone().localize(next_run)

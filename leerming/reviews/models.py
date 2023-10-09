from __future__ import annotations

import datetime as dt
import random
from contextlib import suppress

from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule
from model_utils.models import TimeStampedModel

from .utils import notify_reviewers
from leerming.flashcards.models import FlashCard
from leerming.flashcards.models import Topic
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

    @classmethod
    def get_review_start_message(
        cls, request: HttpRequest, reviewer: User
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
        if cls.get_current_review(reviewer=reviewer, session=request.session):
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

    @classmethod
    def start(cls, review: Review, session: SessionStore) -> Review:
        # if the review is already in the user session then there is nothing to do
        if review.id == session.get(review_id_session_key):
            return review

        cards = list(review.flashcards.values_list("id", flat=True))
        random.shuffle(cards)
        session[review_id_session_key] = review.id
        session[cards_session_key] = list(cards)
        session[current_card_session_key] = cards[0]
        session[answers_session_key] = {}
        return review

    @classmethod
    def end(cls, session: SessionStore) -> None:
        current_review_id = session.get(review_id_session_key)
        try:
            current_review = cls.objects.get(pk=current_review_id)
        except cls.DoesNotExist:
            return
        if current_review.completed_at:
            # the review has already been end, nothing to do
            return

        answers = session.get(answers_session_key)
        completion_date = timezone.now()

        for card_id, correct_answer in answers.items():
            current_review.flashcards.get(id=card_id).review(
                correct_answer=correct_answer, for_date=completion_date.date()
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

        current_review.completed_at = completion_date
        current_review.save()

        # clean session
        session.pop(current_card_session_key)
        session.pop(cards_session_key)
        session.pop(review_id_session_key)
        session.pop(answers_session_key)

        # create reminder for next review
        current_review.reviewer.profile.register_for_next_review()

    @classmethod
    def move_to_next_card(cls, session: SessionStore) -> FlashCard:
        cards = session.get(cards_session_key)
        current_card = session.get(current_card_session_key)

        try:
            next_card = cards[cards.index(current_card) + 1]
        except IndexError as e:
            raise SessionEndedError() from e

        session[current_card_session_key] = next_card

        try:
            return FlashCard.objects.get(pk=next_card)
        except FlashCard.DoesNotExist:
            return cls.move_to_next_card(session)

    @classmethod
    def add_answer(cls, card_id: int, answer: bool, session: SessionStore) -> None:
        answers = session.get(answers_session_key)
        answers[card_id] = answer
        session[answers_session_key] = answers

    @classmethod
    def get_current_card(cls, session: SessionStore) -> tuple[FlashCard, str]:
        current_card_id = session.get(current_card_session_key)
        current_card_index = session.get(cards_session_key).index(current_card_id)
        nbr_of_cards = len(session.get(cards_session_key))
        step = f"{current_card_index + 1}/{nbr_of_cards}"
        return FlashCard.objects.get(pk=current_card_id), step

    @classmethod
    def get_current_review(
        cls, reviewer: User, session: SessionStore | None = None
    ) -> Review | None:
        try:
            if current_review_id := session.get(review_id_session_key):
                return cls.objects.get(pk=current_review_id)
        except AttributeError:
            return
        except ObjectDoesNotExist:
            session.pop(current_card_session_key)
            session.pop(cards_session_key)
            session.pop(review_id_session_key)
            session.pop(answers_session_key)
        with suppress(ObjectDoesNotExist):
            return cls.objects.get(reviewer=reviewer, completed_at__isnull=True)

    @classmethod
    def get_last_review_date(cls, reviewer: User) -> dt.date | None:
        with suppress(AttributeError):
            return (
                cls.objects.filter(reviewer=reviewer, completed_at__isnull=False)
                .order_by("-creation_date")
                .first()
                .creation_date
            )


class ScheduleManager(TimeStampedModel):
    """
    The aim of this model is to group users according to their review session schedule.
      If some users have their next session on the same day, at the same time, they will be grouped so that notifications are sent
     to them all at the same time, instead of one schedule per user.
     This is mainly a way of getting around the fact that sendpulse campaigns are limited to one every 15 minutes.
    """

    reviewers = models.ManyToManyField(User)
    schedule = models.OneToOneField(
        "django_q.Schedule", on_delete=models.SET_NULL, null=True
    )
    result_task = models.OneToOneField(
        "django_q.Task", on_delete=models.CASCADE, null=True
    )

    def __str__(self) -> str:
        if self.schedule:
            return f"will run at {self.schedule.next_run}"
        return f"ran at {self.result_task.started}"

    @classmethod
    def add(cls, reviewer: User, review_datetime: dt.datetime) -> None:
        try:
            manager = cls.objects.get(schedule__next_run=review_datetime)
        except cls.DoesNotExist:
            manager = cls.objects.create()
            schedule = Schedule.objects.create(
                func="leerming.reviews.tasks.run_schedule_manager",
                next_run=review_datetime,
                kwargs={"manager_id": manager.id},
                hook="leerming.reviews.tasks.update_manager_result_task",
            )
            manager.schedule = schedule
            manager.save()

        manager.reviewers.add(reviewer)
        manager.refresh_from_db()

    @classmethod
    def remove(cls, reviewer: User) -> None:
        for manager in cls.objects.filter(reviewers__in=[reviewer]):
            manager.reviewers.remove(reviewer)
            if not manager.reviewers.exists():
                if manager.schedule:
                    manager.schedule.delete()
                manager.delete()

    def notify_reviewers(self):
        date = timezone.now().date()

        reviewers_to_notify = []
        for reviewer in self.reviewers.select_related("profile").all():
            last_review_was_today = (
                Review.get_last_review_date(reviewer=reviewer) == date
            )
            on_going_review = bool(Review.get_current_review(reviewer=reviewer))
            if last_review_was_today or on_going_review:
                continue
            reviewers_to_notify.append(reviewer)

        notify_reviewers(reviewers_to_notify)

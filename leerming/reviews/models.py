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
from .utils import notify_reviewers
from django_q.models import Schedule, Task

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
        if cls.get_current_review(reviewer=reviewer, request=request):
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
    def get_cards_to_review_for(cls, reviewer: User, date: dt.date) -> list[FlashCard]:
        cards = []
        for card in reviewer.flashcards.filter(mastered_at__isnull=True):
            if not card.last_review_date:
                cards.append(card)
            elif card.last_review_date < date - dt.timedelta(days=7**card.level):
                cards.append(card)
        return cards

    @classmethod
    def _get_or_create(cls, reviewer: User, date: dt.date) -> Review:
        if not reviewer.flashcards.filter(mastered_at__isnull=True).filter():
            raise NoCardsToReviewError("No cards to review")

        with suppress(ObjectDoesNotExist):
            return cls.objects.get(reviewer=reviewer, creation_date=date)

        cards = cls.get_cards_to_review_for(reviewer, date)
        if not cards:
            raise NoCardsToReviewError("No cards to review")
        instance = cls.objects.create(reviewer=reviewer, creation_date=date)
        instance.flashcards.set(cards)
        return instance

    @classmethod
    def start(cls, reviewer: User, request: HttpRequest) -> Review:
        review = cls._get_or_create(reviewer, date=dt.date.today())

        # if the review is already in the user session then there is nothing to do
        if request.session.get(review_id_session_key):
            # already started
            return review

        cards = list(review.flashcards.values_list("id", flat=True))
        random.shuffle(cards)
        request.session[review_id_session_key] = review.id
        request.session[cards_session_key] = list(cards)
        request.session[current_card_session_key] = cards[0]
        request.session[answers_session_key] = {}
        return review

    @classmethod
    def end(cls, request: HttpRequest) -> None:
        current_review_id = request.session.get(review_id_session_key)
        try:
            current_review = cls.objects.get(pk=current_review_id)
        except cls.DoesNotExist:
            return
        if current_review.completed_at:
            # the review has already been end, nothing to do
            return

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
        current_review.reviewer.profile.register_for_next_review()

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
    def get_current_card(cls, request: HttpRequest) -> tuple[FlashCard, str]:
        current_card_id = request.session.get(current_card_session_key)
        current_card_index = request.session.get(cards_session_key).index(
            current_card_id
        )
        nbr_of_cards = len(request.session.get(cards_session_key))
        step = f"{current_card_index + 1}/{nbr_of_cards}"
        return FlashCard.objects.get(pk=current_card_id), step

    @classmethod
    def get_current_review(
        cls, reviewer: User, request: HttpRequest | None = None
    ) -> Review | None:
        try:
            if current_review_id := request.session.get(review_id_session_key):
                return cls.objects.get(pk=current_review_id)
        except AttributeError:
            return 
        except ObjectDoesNotExist:
            request.session.pop(current_card_session_key)
            request.session.pop(cards_session_key)
            request.session.pop(review_id_session_key)
            request.session.pop(answers_session_key)
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

    @classmethod
    def get_next_review_datetime(
        cls, reviewer: User, last_review_date: dt.date | None = None
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
        if last_review_date and last_review_date == today:
            next_review_date = last_review_date + dt.timedelta(days=1)
        else:
            next_review_date = today

        # loop until we find a day that matches the next_weekday
        while next_review_date.weekday() != next_weekday:
            next_review_date += dt.timedelta(days=1)

        next_run = dt.datetime.combine(next_review_date, review_time)
        return timezone.make_aware(next_run, timezone.get_current_timezone())



class ScheduleManager(TimeStampedModel):
    """
   The aim of this model is to group users according to their review session schedule.
     If some users have their next session on the same day, at the same time, they will be grouped so that notifications are sent
    to them all at the same time, instead of one schedule per user.
    This is mainly a way of getting around the fact that sendpulse campaigns are limited to one every 15 minutes.
    """

    reviewers = models.ManyToManyField(User)
    schedule = models.OneToOneField("django_q.Schedule", on_delete=models.SET_NULL, null=True)
    result_task = models.OneToOneField("django_q.Task", on_delete=models.CASCADE, null=True)

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
                next_run = review_datetime,
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
                manager.schedule.delete()
                manager.delete()
        


    def notify_reviewers(self):
        date =  timezone.now().date()

        reviewers_to_notify = []
        for reviewer in self.reviewers.all():
            last_review_was_today = Review.get_last_review_date(reviewer=reviewer) == date
            on_going_review = bool(Review.get_current_review(reviewer=reviewer))
            if last_review_was_today or on_going_review:
                continue
            reviewers_to_notify.append(reviewer)
        
        notify_reviewers(reviewers_to_notify)


     


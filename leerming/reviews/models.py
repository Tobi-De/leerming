import datetime as dt
import random
from django.http import HttpRequest
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from leerming.flashcards.models import FlashCard
from leerming.users.models import User
from model_utils.models import TimeStampedModel


from .errors import ReviewCardNotFoundError, NoMoreCardToReviewError, NoCardsToReviewError, ReviewAlreadyStartedError, NoCurrentReviewError


class Review(models.Model):
    """Reviews are made daily, there is only one review per day per user. This constraints 
    are made for the sake of simplicity and to help the user being consistent in his learning.
    """

    flashcards = models.ManyToManyField(FlashCard)
    reviewer = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="reviews"
    )
    score_percentage = models.IntegerField(default=0, verbose_name=_("Score %"))
    creation_date = models.DateField(verbose_name=_("Créé le"), editable=False, default=dt.date.today)
    completed_at = models.DateTimeField(verbose_name=_("Terminé le"), null=True, blank=True)

    class Meta:
        ordering = ("-creation_date",)

    def __str__(self):
        return _(f"Revu du {self.creation_date} - score: {self.score_percentage}%")


    @classmethod
    def compute_score_percentage(cls, score:int, nbr_of_cards:int) -> int:
        return 0 if nbr_of_cards == 0 else round((score / nbr_of_cards) * 100)

    
    @classmethod
    def _get_or_create(cls, user: User) -> "Review":
        today = dt.date.today()

        instance, created = cls.objects.get_or_created(reviewer=user, creation_date=today)
        if not created:
            return instance
    
        cards = FlashCard.objects.filter(mastered_date__isnull=True,last_review_date__lt=today - dt.timedelta(days=7 ** models.F("level")))
        if cards.count() == 0:
            raise NoCardsToReviewError("No cards to review")
        instance.flashcards.add(*cards)
        return instance
    


    @classmethod
    def start(cls, user: User,request:HttpRequest) -> "Review":
        """Start a review for the given user. If a review already exists for today, return it."""
        if request.session.get("current_review"):
            # review already started
            raise ReviewAlreadyStartedError("Review already started")
        review = cls._get_or_create_review(user)
        cards = cards.values_list("id", flat=True)
        random.shuffle(cards)
        request.session["current_review"] = review.id
        request.session["review_cards"] = list(cards)
        request.session["review_current_card"] = cards[0]
        return review

    @classmethod
    def end(cls, request:HttpRequest) -> "Review":
        current_review_id = request.session.get("current_review")
        if not current_review_id:
            raise NoCurrentReviewError("No current review")
        current_review = cls.objects.get(pk=current_review_id)
        current_card = request.session.get("review_current_card")
        review_cards = request.session.get("review_cards")
        if current_card != review_cards[-1]:
            # review not finished
            return
        
        request.session.pop("current_review")
        request.session.pop("review_cards")
        request.session.pop("review_current_card")
        current_review.status = self.Status.DONE
        current_review.save()
        return current_review

    @classmethod
    def next_card(cls, request:HttpRequest)->FlashCard|None:  
        cards = request.session.get("review_cards")
        current_card = request.session.get("review_current_card")
        if not cards or not current_card:
            return None

        try:
            next_card = cards[cards.index(current_card) + 1]
        except IndexError as e:
            raise NoMoreCardToReviewError("No more card to review") from e

        request.session["review_current_card"] = next_card
        return FlashCard.objects.get(pk=next_card)
    
    @classmethod
    def get_current_card_or_404(cls, request:HttpRequest) -> FlashCard:
        current_card_id= request.session.get("review_current_card")
        if not current_card_id:
            raise Http404("No current card")
        try:
            return FlashCard.objects.get(pk=current_card_id)
        except FlashCard.DoesNotExist as e:
            raise ReviewCardNotFoundError("Current card not found") from e



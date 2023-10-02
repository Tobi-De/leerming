from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from leerming.core.utils import render_block_to_string
from leerming.flashcards.models import FlashCard
from .models import Review, NoCardsToReviewError, SessionEndedError


def index(request: HttpRequest):
    return TemplateResponse(
        request,
        "reviews/index.html",
        {
            "reviews": request.user.reviews.all(),
            "start_review_message": Review.get_review_start_message(
                request=request, reviewer=request.user
            ),
        },
    )


def details(request: HttpRequest, review_id: int):
    review = get_object_or_404(request.user.reviews.all(), pk=review_id)
    return TemplateResponse(request, "reviews/details.html", {"review": review})


def no_cards_to_review(request: HttpRequest):
    return TemplateResponse(request, "reviews/no_cards_to_review.html")


@require_http_methods(["POST"])
def start(request: HttpRequest):
    try:
        Review.start(reviewer=request.user, request=request)
    except NoCardsToReviewError:
        return HttpResponseClientRedirect(reverse("reviews:no_cards_to_review"))
    return HttpResponseClientRedirect(reverse("reviews:show_current_card"))


def show_current_card(request: HttpRequest):
    current_review = Review.get_current_review(reviewer=request.user, request=request)
    if not current_review:
        messages.info(request, _("Pas de revision en cours"))
        return redirect("reviews:index")

    try:
        current_card = Review.get_current_card(request)
    except FlashCard.DoesNotExist:
        return redirect("reviews:move_to_next_card")

    return TemplateResponse(
        request, "reviews/show_current_card.html", {"card": current_card}
    )


def reveal_answer(request: HttpRequest):
    return HttpResponse(
        render_block_to_string(
            "reviews/show_current_card.html",
            "answer_revealed",
            context={"card": Review.get_current_card(request)},
        )
    )


answer_field = forms.BooleanField(required=False)


@require_http_methods(["POST"])
def answer_card(request: HttpRequest):
    current_card = Review.get_current_card(request)
    Review.add_answer(
        card_id=current_card.id,
        answer=answer_field.clean(request.POST.get("answer")),
        request=request,
    )
    return redirect("reviews:move_to_next_card")


def move_to_next_card(request: HttpRequest):
    try:
        Review.move_to_next_card(request)
    except SessionEndedError:
        return HttpResponseClientRedirect(reverse("reviews:end"))
    return HttpResponseClientRedirect(reverse("reviews:show_current_card"))


def end(request: HttpRequest):
    Review.end(request)
    return TemplateResponse(request, "reviews/end.html")

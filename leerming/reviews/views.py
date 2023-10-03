from django import forms
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from .models import NoCardsToReviewError
from .models import Review
from .models import SessionEndedError
from leerming.core.utils import render_block_to_string
from leerming.flashcards.models import FlashCard


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
    return TemplateResponse(
        request,
        "reviews/no_cards_to_review.html",
        {"no_cards": not request.user.flashcards.exists()},
    )


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
        raise Http404(_("No review in progress"))

    try:
        current_card, step = Review.get_current_card(request)
    except FlashCard.DoesNotExist:
        return redirect("reviews:move_to_next_card")

    return TemplateResponse(
        request, "reviews/show_current_card.html", {"card": current_card, "step": step}
    )


def reveal_answer(request: HttpRequest):
    current_card, _ = Review.get_current_card(request)
    return HttpResponse(
        render_block_to_string(
            "reviews/show_current_card.html",
            "answer_revealed",
            context={"card": current_card},
        )
    )


answer_field = forms.BooleanField(required=False)


@require_http_methods(["POST"])
def answer_card(request: HttpRequest):
    current_card, _ = Review.get_current_card(request)
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

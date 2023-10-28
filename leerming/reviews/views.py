from django import forms
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from leerming.flashcards.models import FlashCard
from leerming.users.models import User
from .forms import ReviewForm
from .models import Review
from .models import SessionEndedError


def _get_current_review_or_404(user: User) -> Review:
    if current_review := Review.get_current_review(reviewer=user):
        return current_review
    raise Http404(_("No review in progress"))


def index(request: HttpRequest):
    return TemplateResponse(
        request,
        "reviews/index.html",
        {
            "reviews": request.user.reviews.prefetch_related("topics"),
            "start_review_message": Review.get_review_start_message(
                reviewer=request.user,
                current_review=Review.get_current_review(reviewer=request.user),
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


def start(request: HttpRequest):
    if Review.get_current_review(reviewer=request.user):
        return redirect("reviews:show_current_card")

    if uncompleted_review := request.user.reviews.filter(
        completed_at__isnull=True
    ).first():
        uncompleted_review.start()
        return HttpResponseClientRedirect(reverse("reviews:show_current_card"))

    today = timezone.now().date()
    form = ReviewForm(request=request, creation_date=today)
    if request.method == "POST":
        form = ReviewForm(request.POST, request=request, creation_date=today)
        if form.is_valid():
            review = form.save()
            review.start()
            return HttpResponseClientRedirect(reverse("reviews:show_current_card"))
    template_name = "reviews/start.html#form" if request.htmx else "reviews/start.html"
    return TemplateResponse(
        request, template_name, {"form": form, "review_date": today}
    )


def show_current_card(request: HttpRequest):
    current_review = _get_current_review_or_404(request.user)
    try:
        current_card, step = current_review.get_current_card()
    except FlashCard.DoesNotExist:
        return redirect("reviews:move_to_next_card")

    return TemplateResponse(
        request, "reviews/show_current_card.html", {"card": current_card, "step": step}
    )


def reveal_answer(request: HttpRequest):
    current_review = _get_current_review_or_404(request.user)
    current_card, _ = current_review.get_current_card()
    return TemplateResponse(
        request,
        "reviews/show_current_card.html#answer_revealed",
        {"flashcard": current_card},
    )


answer_field = forms.BooleanField(required=False)


@require_http_methods(["POST"])
def answer_card(request: HttpRequest):
    current_review = _get_current_review_or_404(request.user)
    current_card, _ = current_review.get_current_card()
    current_review.add_answer(
        card_id=current_card.id, answer=answer_field.clean(request.POST.get("answer"))
    )
    return redirect("reviews:move_to_next_card")


def move_to_next_card(request: HttpRequest):
    current_review = _get_current_review_or_404(request.user)
    try:
        current_review.move_to_next_card()
    except SessionEndedError:
        return HttpResponseClientRedirect(reverse("reviews:end"))
    return redirect("reviews:show_current_card")


def end(request: HttpRequest):
    current_review = _get_current_review_or_404(request.user)
    current_review.end()
    return TemplateResponse(request, "reviews/end.html")

from django.http import HttpRequest
from django.template.response import TemplateResponse

from .models import Review
from .errors import ReviewCardNotFoundError, NoCardsToReviewError, NoMoreCardToReviewError
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# start (check if review for today exists, if yes, show page "keep it one review a day"),
# if no create check if there is a current review if yes return to it else create a new one

def index(request: HttpRequest):
    return TemplateResponse(request, "reviews/index.html", {"reviews": request.user.reviews.all()})

def details(request: HttpRequest, review_id: int):
    review = get_object_or_404(request.user.reviews.all(), pk=review_id)
    return TemplateResponse(request, "reviews/details.html", {"review": review})

def start(request: HttpRequest):
    try:
        Review.start(user=request.user, request=request)
    except NoCardsToReviewError as e:
        return redirect("reviews:index")
    return TemplateResponse(request, "reviews/start.html", {"review": review})


def show_card(request: HttpRequest):
    try:
        current_card = Review.get_current_card(request)
    except NoCardsToReviewError as e:
        return TemplateResponse(request, "reviews/no_cards_to_review.html")
    return TemplateResponse(request, "reviews/show_card.html", {"card": current_card})

@require_http_methods(["POST"])
def answer_card(request: HttpRequest):
    current_card = Review.get_current_card(request)
    current_card.review(correct_answer=request.POST.get("correct_answer"))
    return redirect("reviews:next_card")


def next_card(request: HttpRequest):
    try:
        current_card = Review.next_card(request)
    except NoMoreCardToReviewError as e:
        review = Review.end(request)
        return redirect(reverse("reviews:details", args=[review.id])))
        
    return redirect("reviews:show_card")
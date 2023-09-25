from django.http import HttpRequest
from django.template.response import TemplateResponse

from .models import Review


def index(request: HttpRequest):
    reviews = Review.objects.filter(reviewer=request.user)
    return TemplateResponse(request, "reviews/index.html", {"reviews": reviews})

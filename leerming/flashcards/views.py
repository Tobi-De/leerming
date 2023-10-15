from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from .filters import FilterForm
from .forms import FlashCard
from .forms import FlashCardCreateForm
from .forms import FlashCardEditForm


def index(request: HttpRequest):
    form = FilterForm(request.GET or None, request=request)
    flashcards = form.filter()
    flashcards = flashcards.order_by(models.F("next_review_date").asc(nulls_first=True))
    paginator = Paginator(flashcards, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template_name = (
        "flashcards/index.html#flashcards" if request.htmx else "flashcards/index.html"
    )
    return TemplateResponse(
        request,
        template_name,
        {
            "page_obj": page_obj,
            "total_count": flashcards.count(),
            "form": form,
        },
    )


def create(request: HttpRequest):
    form = FlashCardCreateForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        form.instance.owner = request.user
        form.save()
        next_url = (
            "flashcards:create"
            if form.cleaned_data["return_to_add_new"]
            else "flashcards:index"
        )
        return HttpResponseClientRedirect(reverse(next_url))
    template_name = (
        "flashcards/create.html#form" if request.htmx else "flashcards/create.html"
    )
    return TemplateResponse(request, template_name, {"form": form})


def edit(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    form = FlashCardEditForm(
        instance=flashcard, data=request.POST or None, request=request
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponseClientRedirect(reverse("flashcards:index"))
    template_name = (
        "flashcards/edit.html#form" if request.htmx else "flashcards/edit.html"
    )
    return TemplateResponse(
        request, template_name, {"flashcard": flashcard, "form": form}
    )


def show_question(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    return TemplateResponse(
        request, "flashcards/index.html#card_question", {"flashcard": flashcard}
    )


def show_answer(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    return TemplateResponse(
        request, "flashcards/index.html#card_answer", {"flashcard": flashcard}
    )


@require_http_methods(["POST"])
def delete(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    flashcard.delete()
    return HttpResponseClientRedirect(reverse("flashcards:index"))

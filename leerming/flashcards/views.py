from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from render_block import render_block_to_string

from leerming.core.utils import for_htmx
from .forms import FlashCard
from .forms import FlashCardCreateForm
from .forms import FlashCardEditForm


def index(request: HttpRequest):
    flashcards = FlashCard.objects.filter(owner=request.user)
    return TemplateResponse(
        request, "flashcards/index.html", {"flashcards": flashcards}
    )


@for_htmx(use_block="form")
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
    return TemplateResponse(request, "flashcards/create.html", {"form": form})


@for_htmx(use_block="form")
def edit(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    form = FlashCardEditForm(
        instance=flashcard, data=request.POST or None, request=request
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponseClientRedirect(reverse("flashcards:edit", args=[pk]))
    return TemplateResponse(
        request, "flashcards/edit.html", {"flashcard": flashcard, "form": form}
    )


def show_question(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    return HttpResponse(
        render_block_to_string(
            "flashcards/index.html", "card_question", {"flashcard": flashcard}
        )
    )


def show_answer(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    return HttpResponse(
        render_block_to_string(
            "flashcards/index.html", "card_answer", {"flashcard": flashcard}
        )
    )


@require_http_methods(["POST"])
def delete(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    flashcard.delete()
    return HttpResponseClientRedirect(reverse("flashcards:index"))

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from leerming.core.utils import for_htmx
from .forms import FlashCard, FlashCardCreateForm, FlashCardEditForm


def index(request: HttpRequest):
    flashcards = FlashCard.objects.filter(owner=request.user)
    return TemplateResponse(
        request, "flashcards/index.html", {"flashcards": flashcards}
    )


@for_htmx(use_block="form")
def create(request: HttpRequest):
    form = FlashCardCreateForm(request.POST or None)
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
    form = FlashCardEditForm(instance=flashcard, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponseClientRedirect(reverse("flashcards:edit", args=[pk]))
    return TemplateResponse(
        request, "flashcards/edit.html", {"flashcard": flashcard, "form": form}
    )


def show_question(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    html = f""" <a href="#"  hx-swap="outerHTML" hx-get="{reverse('flashcards:show_answer', args=[pk])}" hx-target="this">
              <h3 class="mb-2 text-sm font-bold tracking-tight text-gray-900 dark:text-white">{flashcard}</h3>
            </a>"""
    return HttpResponse(html)


def show_answer(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    html = f"""<a href="#"  hx-swap="outerHTML" hx-get="{reverse('flashcards:show_question', args=[pk])}" hx-target="this">
                <h3 class="mb-2 text-sm font-bold tracking-tight text-green-400">{flashcard.answer_display}</h3>
              </a>"""
    return HttpResponse(html)


@require_http_methods(["POST"])
def delete(request: HttpRequest, pk: int):
    flashcard = get_object_or_404(FlashCard.objects.filter(owner=request.user), pk=pk)
    flashcard.delete()
    return HttpResponseClientRedirect(reverse("flashcards:index"))

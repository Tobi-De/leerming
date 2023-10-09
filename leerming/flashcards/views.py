from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from .forms import FlashCard
from .forms import FlashCardCreateForm
from .forms import FlashCardEditForm
from django.core.paginator import Paginator

def index(request: HttpRequest):
    flashcards = FlashCard.objects.filter(owner=request.user)
    paginator = Paginator(flashcards, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return TemplateResponse(
        request, "flashcards/index.html", {"page_obj": page_obj}
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

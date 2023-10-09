from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from watson import search

from .forms import FlashCard
from .forms import FlashCardCreateForm
from .forms import FlashCardEditForm
from leerming.users.models import User

ALL_TOPICS = "ALL_TOPICS"
NO_TOPIC = "NO_TOPIC"


def _get_topic_options(user: User):
    return [(ALL_TOPICS, _("Tous les sujets")), (NO_TOPIC, _("Sans sujet"))] + [
        (topic.id, topic.title) for topic in user.topics.all()
    ]


def _search_flashcards(
    user: User, topic: str, query: str | None = None
) -> QuerySet[FlashCard]:
    results = FlashCard.objects.filter(owner=user)
    if query:
        results = search.filter(results, query)
    if topic == ALL_TOPICS:
        return results
    if topic == NO_TOPIC:
        return results.filter(topic__isnull=True)

    return results.filter(topic_id=topic)


def index(request: HttpRequest):
    flashcards = _search_flashcards(
        user=request.user,
        topic=request.GET.get("topic", ALL_TOPICS),
        query=request.GET.get("query"),
    )
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
            "topic_options": _get_topic_options(request.user),
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

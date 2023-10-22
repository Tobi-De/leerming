from django.core.paginator import Paginator
from django.db import models
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect

from ..documents.models import UploadedDocument
from .filters import FilterForm
from .forms import FlashCardCreateForm
from .forms import FlashCardEditForm
from .forms import FlashCardFromDocument
from .forms import LLMFlashCard
from .llm_utils import delete_llm_flashcards_from_session
from .llm_utils import load_llm_flashcards_from_session
from .llm_utils import make_flashcards_from
from .llm_utils import save_llm_flashcards_to_session
from .models import FlashCard
from .models import Topic


def index(request: HttpRequest):
    form = FilterForm(request.GET or None, request=request)
    flashcards = form.filter()
    flashcards = flashcards.order_by(
        models.F("next_review_date").asc(nulls_first=True), "-created"
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


def create_from_document(request: HttpRequest):
    form = FlashCardFromDocument(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        topic = form.cleaned_data["topic"]
        document: UploadedDocument = form.cleaned_data["document"]
        focus_on = form.cleaned_data["focus_on"]
        result = make_flashcards_from(
            source_text=document.get_relevant_text_for(focus_on),
            main_focus_point=focus_on,
            card_type=form.cleaned_data["card_type"],
            topic_id=topic.id if topic else None,
        )
        save_llm_flashcards_to_session(request, result)
        return HttpResponseClientRedirect(reverse("flashcards:triage"))

    return TemplateResponse(
        request,
        "flashcards/create_from_document.html",
        {"form": FlashCardFromDocument(request=request)},
    )


def triage(request: HttpRequest):
    if flashcards := load_llm_flashcards_from_session(request):
        return TemplateResponse(
            request, "flashcards/triage.html", {"flashcards": flashcards}
        )
    raise Http404()


def edit_llm_flashcard(request: HttpRequest, id: str):
    flashcards = load_llm_flashcards_from_session(request)
    flashcard = [flashcard for flashcard in flashcards if flashcard.id == id][0]
    form = LLMFlashCard(
        request.POST or None,
        initial={
            "question": flashcard.question,
            "answer": flashcard.answer,
            "card_type": flashcard.card_type,
        },
    )
    if request.POST and form.is_valid():
        flashcard.question = form.cleaned_data["question"]
        flashcard.answer = form.cleaned_data["answer"]
        save_llm_flashcards_to_session(request, flashcards)
        return HttpResponseClientRedirect(reverse("flashcards:triage"))
    return TemplateResponse(
        request,
        "flashcards/triage.html#edit_flashcard",
        {
            "form": form,
            "url": reverse("flashcards:edit_llm_flashcard", kwargs={"id": id}),
        },
    )


@require_http_methods(["POST"])
def save_llm_flashcards(request: HttpRequest):
    flashcards = load_llm_flashcards_from_session(request)
    selected_flashcards = request.POST.getlist("selected_flashcards")
    db_flashcards = [
        FlashCard(
            question=flashcard.question,
            answer=flashcard.answer,
            owner=request.user,
            card_type=flashcard.card_type,
        )
        for flashcard in flashcards
        if flashcard.id in selected_flashcards
    ]
    if topic_id := flashcards[0].topic_id:
        topic = Topic.objects.get(id=topic_id)
        for f in db_flashcards:
            f.topic = topic

    FlashCard.objects.bulk_create(db_flashcards, ignore_conflicts=True)
    delete_llm_flashcards_from_session(request)
    return redirect("flashcards:index")

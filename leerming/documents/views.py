from django.db import IntegrityError
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django_htmx.http import reswap
from django_htmx.http import retarget
from django_htmx.http import trigger_client_event
from django_q.tasks import async_task
from django_q.tasks import result

from .forms import UploadForm
from .models import UploadedDocument
from leerming.users.models import User


def _create_document(doc_type: str, owner_id: int, params: dict) -> int | None:
    owner = User.objects.get(id=owner_id)
    create_func = UploadedDocument.get_create_func(doc_type)
    try:
        doc = create_func(owner=owner, **params)
        return doc.id
    except IntegrityError:
        return


def select(request: HttpRequest):
    documents = request.user.uploaded_documents.all().order_by("-created")
    response = TemplateResponse(
        request,
        "documents/select.html",
        {
            "documents": documents,
            "selected": int(request.GET.get("selected", default=documents.first().id)),
        },
    )
    if new_target := request.GET.get("retarget"):
        response = retarget(response, f"#{new_target}")
    return trigger_client_event(response, "showSubmitBtn", {})


def upload(request: HttpRequest):
    data = (request.POST, request.FILES) if request.method == "POST" else (None, None)
    form = UploadForm(*data, context={"user": request.user})
    if form.is_valid():
        cleaned_data = form.cleaned_data
        task_id = async_task(
            _create_document,
            doc_type=cleaned_data.pop("doc_type"),
            owner_id=request.user.id,
            params=cleaned_data,
        )
        return redirect(reverse("documents:upload_progress", args=[task_id]))
    response = TemplateResponse(
        request,
        "documents/upload.html",
        {
            "form": form,
            "user_has_existing_documents": request.user.uploaded_documents.exists(),
        },
    )
    if not form.is_valid() and request.method == "POST":
        response = retarget(response, "#upload-card")
        return reswap(response, "outerHTML")
    return trigger_client_event(response, "hideSubmitBtn", {})


def upload_progress(request: HttpRequest, task_id: str):
    return TemplateResponse(
        request, "documents/upload_progress.html", {"task_id": task_id}
    )


#  try for 6 min max for now, query for the result every 3 seconds with a max of 120 attempts
MAX_NBR_OF_TRY = 120
MILLISECONDS_WAIT = 3000


def upload_status(request: HttpRequest, task_id: str):
    nbr_of_try = request.session.get("nbr_of_try", 1)
    select_url = reverse("documents:select") + "?retarget=upload-card"
    if nbr_of_try > MAX_NBR_OF_TRY:
        # maybe add a message to tell the user to retry or check if task failed
        del request.session["nbr_of_try"]
        return redirect(select_url)
    request.session["nbr_of_try"] = nbr_of_try + 1
    if document_id := result(task_id, MILLISECONDS_WAIT):
        del request.session["nbr_of_try"]
        return redirect(f"{select_url}&selected={document_id}")
    return redirect(reverse("documents:upload_progress", args=[task_id]))


def get_form(request: HttpRequest):
    return HttpResponse(UploadForm(initial=request.GET).render())


def index(request: HttpRequest):
    if request.user.uploaded_documents.exists():
        return redirect("documents:select")
    return redirect("documents:upload")

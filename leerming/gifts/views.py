from django.db import models
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from django_htmx.http import retarget

from .forms import GiftForm
from .models import Gift
from leerming.flashcards.filters import FilterForm as FlashCardFilterForm
from leerming.users.models import User

GIFT_PARAMS_SESSION_KEY = "gift_params"


def set_recipient(request: HttpRequest):
    form = GiftForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if FlashCardFilterForm(request.POST, request=request).filter().count() == 0:
            form.add_error(None, "Vous ne pouvez pas envoyer un cadeau sans carte.")
            return retarget(HttpResponse(form.render()), "#dialog-form")
        request.session[GIFT_PARAMS_SESSION_KEY] = request.POST
        return redirect("gifts:confirm_send")

    return HttpResponse(form.render())


def confirm_send(request: HttpRequest):
    data = dict(request.session[GIFT_PARAMS_SESSION_KEY])
    recipient_email = data.pop("recipient_email")
    flashcards = FlashCardFilterForm(data, request=request).filter()
    if request.method == "POST":
        Gift.create(
            sender=request.user,
            recipient=User.objects.get(email=recipient_email),
            flashcards=flashcards,
        )
        return HttpResponseClientRedirect(reverse("gifts:index"))
    return TemplateResponse(
        request,
        "gifts/confirm_send.html",
        {
            "flashcard_count": flashcards.count(),
            "recipient_email": recipient_email,
            "topic_list": flashcards.exclude(topic__isnull=True)
            .values_list("topic__title", flat=True)
            .distinct(),
        },
    )


def index(request: HttpRequest):
    return TemplateResponse(
        request,
        "gifts/index.html",
        {
            "gifts": Gift.objects.filter(
                models.Q(sender=request.user) | models.Q(recipient=request.user)
            )
            .select_related("sender", "recipient")
            .annotate(
                sent_by_user=models.Case(
                    models.When(sender=request.user, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                )
            )
            .order_by("-created")
        },
    )


@require_http_methods(["POST"])
def open_gift(request: HttpRequest, pk: int):
    gift = get_object_or_404(Gift, pk=pk)
    gift.open()
    return HttpResponseClientRedirect(reverse("flashcards:index"))


@require_http_methods(["POST"])
def cancel_send(request: HttpRequest):
    request.session.pop(GIFT_PARAMS_SESSION_KEY, None)
    return HttpResponseClientRedirect(reverse("flashcards:index"))

from django import forms
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from .models import Review
from leerming.flashcards.models import Topic


NO_TOPIC_FLASHCARD = "no_topic"


class ReviewForm(forms.Form):
    topics = forms.MultipleChoiceField(
        label="", widget=forms.CheckboxSelectMultiple(), required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.creation_date = kwargs.pop("creation_date")
        super().__init__(*args, **kwargs)
        self.fields["topics"].choices = [
            (NO_TOPIC_FLASHCARD, _("Cartes sans sujet"))
        ] + [(topic.id, topic.title) for topic in self.request.user.topics.all()]

    def clean_topics(self) -> tuple[QuerySet[Topic], None | str]:
        cleaned_data = self.cleaned_data
        topics = cleaned_data["topics"]
        if not topics:
            return Topic.objects.none(), None

        include_no_topic_cards = (
            NO_TOPIC_FLASHCARD if NO_TOPIC_FLASHCARD in topics else None
        )
        return (
            self.request.user.topics.filter(
                id__in=(t for t in topics if t != NO_TOPIC_FLASHCARD)
            ),
            include_no_topic_cards,
        )

    def clean(self):
        cleaned_data = super().clean()
        topics, include_no_topic_cards = cleaned_data["topics"]

        # see if there is flashcards to review
        flashcards = Review.get_flashcards_to_review_for(
            reviewer=self.request.user, date=self.creation_date
        )

        filters = Q()
        if topics.exists():
            filters |= Q(topic__in=topics)
        if include_no_topic_cards:
            filters |= Q(topic__isnull=True)

        flashcards = flashcards.filter(filters)

        if not flashcards.exists():
            msg = _("Aucune carte à réviser pour aujourd'hui")
            if topics:
                msg = _(
                    f"Aucune carte à réviser aujourd'hui pour les sujets: {', '.join(topics.values_list('title', flat=True))}"
                )
            raise forms.ValidationError(msg)
        return {
            "topics": topics,
            "reviewer": self.request.user,
            "flashcards": flashcards,
            "creation_date": self.creation_date,
        }

    def save(self) -> Review:
        return Review.get_or_create(**self.cleaned_data)

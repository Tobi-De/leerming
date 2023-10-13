from django import forms
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from watson import search

from .models import FlashCard
from leerming.flashcards.models import Topic

ALL_TOPICS = "ALL_TOPICS"
NO_TOPIC = "NO_TOPIC"
ALL_DIFFICULTIES = "ALL_DIFFICULTIES"
MASTERED_OR_NOT = "MASTERED_OR_NOT"
NOT_MASTERED = "NOT_MASTERED"
MASTERED = "MASTERED"


def _get_topic_choices(topics: QuerySet[Topic]):
    return [(ALL_TOPICS, _("Tous les sujets")), (NO_TOPIC, _("Sans sujet"))] + [
        (topic.id, topic.title) for topic in topics
    ]


def _get_difficulty_choices():
    return [(ALL_DIFFICULTIES, _("Tous les niveaux"))] + [
        (level, _(f"Niveau {label}")) for level, label in FlashCard.Difficulty.choices
    ]


class FilterForm(forms.Form):
    template_name = "flashcards/filter_form.html"

    query = forms.CharField(required=False)
    topic = forms.ChoiceField()
    difficulty = forms.ChoiceField()
    next_review_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    mastered = forms.ChoiceField(
        choices=[
            (MASTERED_OR_NOT, _("Tous")),
            (MASTERED, _("Maitrisé")),
            (NOT_MASTERED, _("Non Maitrisé")),
        ]
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.user = self.request.user
        super().__init__(*args, **kwargs)
        self.fields["topic"].choices = _get_topic_choices(self.user.topics.all())
        self.fields["difficulty"].choices = _get_difficulty_choices()

    def filter(self) -> QuerySet[FlashCard]:
        queryset = self.user.flashcards.select_related("topic")
        if not self.is_valid():
            return queryset
        query = self.cleaned_data["query"]
        topic = self.cleaned_data["topic"]
        difficulty = self.cleaned_data["difficulty"]
        next_review_date = self.cleaned_data["next_review_date"]
        mastered = self.cleaned_data["mastered"]

        if query:
            queryset = search.filter(queryset, query)
        if next_review_date:
            queryset = queryset.filter(next_review_date=next_review_date)

        if topic == ALL_TOPICS:
            topic_filter = Q()
        elif topic == NO_TOPIC:
            topic_filter = Q(topic__isnull=True)
        else:
            topic_filter = Q(topic_id=topic)

        if difficulty == ALL_DIFFICULTIES:
            difficulty_filter = Q()
        else:
            difficulty_filter = Q(difficulty=difficulty)

        if mastered == MASTERED_OR_NOT:
            mastered_filter = Q()
        elif mastered == NOT_MASTERED:
            mastered_filter = Q(mastered_at__isnull=True)
        else:
            mastered_filter = Q(mastered_at__isnull=False)

        return queryset.filter(topic_filter & difficulty_filter & mastered_filter)

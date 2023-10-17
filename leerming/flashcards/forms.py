from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from .models import FlashCard
from .models import Topic


class NoValidationChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class FlashCardForm(forms.ModelForm):
    topic = NoValidationChoiceField(
        label=_("Sujet"),
        widget=forms.Select(attrs={"class": "tom-select"}),
        required=False,
        help_text=_(
            "Si le sujet n'existe pas, soyer certain de cliquer sur ajouter/entrée pour qu'il soit créé"
        ),
    )

    class Meta:
        model = FlashCard
        fields = ("card_type", "question", "answer", "difficulty", "topic")
        widgets = {
            "question": forms.Textarea(attrs={"rows": 2}),
            "answer": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["topic"].choices = [(None, _("Aucun"))] + [
            (t.id, t.title) for t in Topic.objects.filter(created_by=self.request.user)
        ]

    def clean_topic(self):
        if topic := self.cleaned_data.pop("topic"):
            try:
                topic_id = int(topic)
            except ValueError:
                topic, _ = Topic.objects.get_or_create(
                    title=topic.capitalize(), created_by=self.request.user
                )
            else:
                topic = Topic.objects.get(id=topic_id)
            return topic
        return None

    def clean(self):
        cleaned_data = self.cleaned_data

        if (
            cleaned_data["card_type"] == FlashCard.CardType.FILL_IN_THE_GAP
            and cleaned_data["answer"] not in cleaned_data["question"]
        ):
            self.add_error(
                field="answer",
                error=_(
                    "La réponse doit être dans la question pour une carte de type Remplissage"
                ),
            )

        duplicate_check_query = models.Q(
            question=cleaned_data["question"],
            answer=cleaned_data["answer"],
            owner=self.request.user,
        )
        if self.instance:
            duplicate_check_query = duplicate_check_query & ~models.Q(
                pk=self.instance.pk
            )
        if FlashCard.objects.filter(duplicate_check_query).exists():
            self.add_error(
                None, _("Une carte avec cette question et cette réponse existe déjà.")
            )
        return cleaned_data


class FlashCardCreateForm(FlashCardForm):
    return_to_add_new = forms.BooleanField(
        initial=False,
        required=False,
        label=_("Après ajout, revenir et ajouter une nouvelle carte"),
    )

    class Meta(FlashCardForm.Meta):
        fields = ("card_type", "question", "answer", "topic", "return_to_add_new")


class FlashCardEditForm(FlashCardForm):
    def save(self, commit=True):
        instance: FlashCard = super().save(commit=commit)
        if "difficulty" in self.changed_data:
            instance.update_level_from_difficulty()
        return instance


class FlashCardFromDocument(FlashCardForm):
    document = forms.CharField(widget=forms.Textarea())
    focus_on = forms.CharField(
        label=_("Point central"),
        help_text=_(
            "Cette question servira a orienter l'IA sur le 'sujet' des cartes générées, sur quoi les cartes porteront-elles ?"
        ),
    )

    class Meta:
        model = FlashCard
        fields = ("card_type", "topic", "focus_on", "document")
        widgets = {
            "question": forms.Textarea(attrs={"rows": 2}),
            "answer": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        return self.cleaned_data


class LLMFlashCard(forms.ModelForm):

    card_type = forms.CharField(label="",widget=forms.HiddenInput())
    class Meta:
        model = FlashCard
        fields = ("question", "answer", "card_type")
        widgets = {
            "question": forms.Textarea(attrs={"rows": 2}),
            "answer": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned_data = self.cleaned_data

        if (
            cleaned_data["card_type"] == FlashCard.CardType.FILL_IN_THE_GAP
            and cleaned_data["answer"] not in cleaned_data["question"]
        ):
            self.add_error(
                field="answer",
                error=_(
                    "La réponse doit être dans la question pour une carte de type Remplissage"
                ),
            )
        return cleaned_data
    


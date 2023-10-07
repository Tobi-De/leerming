from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FlashCard, Topic


class NoValidationChoiceField(forms.ChoiceField):
    def validate(self, value):
        pass


class FlashCardForm(forms.ModelForm):
    topic = NoValidationChoiceField(
        label=_("Sujet"),
        widget=forms.Select(attrs={"class": "tom-select"}),
        required=False,
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

    def clean(self):
        cleaned_data = self.cleaned_data

        if topic := self.cleaned_data.pop("topic"):
            try:
                topic_id = int(topic)
            except ValueError:
                topic = Topic.objects.create(
                    title=topic.capitalize(), created_by=self.request.user
                )
            else:
                print("here")
                topic = Topic.objects.get(id=topic_id)
                print(topic)
            self.instance.topic = topic

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

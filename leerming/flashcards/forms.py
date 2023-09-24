from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FlashCard


class FlashCardForm(forms.ModelForm):
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


class FlashCardCreateForm(FlashCardForm):
    return_to_add_new = forms.BooleanField(
        initial=False,
        required=False,
        label=_("Après ajout, revenir et ajouter une nouvelle carte"),
    )

    class Meta:
        model = FlashCard
        fields = ("card_type", "question", "answer", "return_to_add_new")


class FlashCardEditForm(FlashCardForm):
    class Meta:
        model = FlashCard
        fields = ("card_type", "question", "answer", "level")

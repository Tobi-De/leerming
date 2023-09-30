from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FlashCard


class FlashCardForm(forms.ModelForm):
    # template_name = "forms/flashcard.html"

    class Meta:
        model = FlashCard
        fields = ("card_type", "question", "answer", "level")
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


class FlashCardCreateForm(FlashCardForm):
    return_to_add_new = forms.BooleanField(
        initial=False,
        required=False,
        label=_("Après ajout, revenir et ajouter une nouvelle carte"),
    )

    class Meta(FlashCardForm.Meta):
        fields = ("card_type", "question", "answer", "return_to_add_new")


class FlashCardEditForm(FlashCardForm):
    pass

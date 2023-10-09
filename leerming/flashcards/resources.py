from import_export import fields
from import_export import widgets
from import_export.resources import ModelResource

from leerming.flashcards.models import FlashCard
from leerming.users.models import User


class FlashCardResource(ModelResource):
    owner = fields.Field(
        column_name="owner",
        attribute="owner",
        widget=widgets.ForeignKeyWidget(User, field="email"),
    )

    class Meta:
        model = FlashCard
        import_id_fields = ("card_type", "owner", "question")
        fields = (
            "id",
            "card_type",
            "question",
            "answer",
            "level",
            "owner",
            "mastered_at",
        )

    def dehydrate_id(self, _):
        return None

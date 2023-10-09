from django.apps import AppConfig
from watson import search


class CardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "leerming.flashcards"

    def ready(self):
        search.register(self.get_model("FlashCard"), fields=("question", "answer"))

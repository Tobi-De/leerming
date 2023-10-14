from django.db import models

from model_utils.models import TimeStampedModel
from django.db.models import QuerySet
from leerming.users.models import User
from leerming.flashcards.models import FlashCard
from django.utils import timezone

class Gift(TimeStampedModel):
    sender = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="gifts_sent")
    recipient = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="gifts_received")
    flashcards = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.sender} -> {self.recipient}"
    
    def process(self):
        for flashcard in self.flashcards:
            FlashCard.objects.create(
                owner=self.recipient,
                question=flashcard["question"],
                answer=flashcard["answer"],
                topic__title=flashcard["topic__title"],
            )
        self.processed_at = timezone.now()
        self.save()
    
    @classmethod
    def create(self, sender:User, recipient:User, flashcards:QuerySet[FlashCard]):
        json_flashcards = flashcards.values("question", "answer", "topic__title")
        return self.objects.create(sender=sender, recipient=recipient, flashcards=json_flashcards)


    
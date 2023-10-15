from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from leerming.flashcards.models import FlashCard
from leerming.flashcards.models import Topic
from leerming.users.models import User


def _get_topic(title: str | None, topics: list[Topic]) -> Topic | None:
    if not title:
        return
    return [topic for topic in topics if topic.title == title][0]


class Gift(TimeStampedModel):
    sender = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="gifts_sent"
    )
    recipient = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="gifts_received"
    )
    flashcards = models.JSONField()
    opened_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.sender} -> {self.recipient}"

    @property
    def topic_list(self) -> list[str]:
        tp_list = [flashcard["topic__title"] for flashcard in self.flashcards]
        if None in tp_list:
            tp_list.append(_("Sans sujet"))
            tp_list = [t for t in tp_list if t]
        return list(set(tp_list))

    @property
    def flashcard_count(self) -> int:
        return len(self.flashcards)

    def open(self) -> None:
        Topic.objects.bulk_create(
            (
                Topic(title=flashcard["topic__title"], created_by=self.recipient)
                for flashcard in self.flashcards
                if flashcard["topic__title"]
            ),
            ignore_conflicts=True,
        )
        # for some reason the return values of the bulk create does not have ids
        db_topics = list(
            Topic.objects.filter(
                created_by=self.recipient,
                title__in={flashcard["topic__title"] for flashcard in self.flashcards},
            )
        )
        unsaved_flashcards = [
            FlashCard(
                owner=self.recipient,
                question=flashcard["question"],
                answer=flashcard["answer"],
                topic=_get_topic(flashcard["topic__title"], db_topics),
            )
            for flashcard in self.flashcards
        ]
        FlashCard.objects.bulk_create(unsaved_flashcards, ignore_conflicts=True)
        self.opened_at = timezone.now()
        self.save()

    @classmethod
    def create(cls, sender: User, recipient: User, flashcards: QuerySet[FlashCard]):
        json_flashcards = list(flashcards.values("question", "answer", "topic__title"))
        return cls.objects.create(
            sender=sender, recipient=recipient, flashcards=json_flashcards
        )

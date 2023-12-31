from dataclasses import asdict
from dataclasses import dataclass
from functools import cached_property

from django.http import HttpRequest
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

from ..models import FlashCard
from .prompts import clozed_delete_template
from .prompts import clozed_deletion_output_parser
from .prompts import front_back_output_parser
from .prompts import front_back_template
from .prompts import ParsedCard

clozed_deletion_chain = (
    clozed_delete_template | OpenAI() | clozed_deletion_output_parser
)
front_back_chain = front_back_template | ChatOpenAI() | front_back_output_parser

CHAINS_TO_CARD_TYPE = {
    FlashCard.CardType.FILL_IN_THE_GAP: clozed_deletion_chain,
    FlashCard.CardType.FRONT_BACK: front_back_chain,
}


@dataclass
class LLMFlashCard:
    id: str
    question: str
    answer: str
    card_type: str
    topic_id: str | None = None

    @cached_property
    def split_on_answer(self):
        return self.question.split(self.answer)

    @property
    def before_answer(self):
        return self.split_on_answer[0]

    @property
    def after_answer(self):
        return self.split_on_answer[1]


def make_flashcards_from(
    source_text: str,
    key_question: str,
    card_type: str,
    max_result: int = 10,
    topic_id: int | None = None,
) -> list[LLMFlashCard]:
    chain = CHAINS_TO_CARD_TYPE[card_type]
    parsed_cards: list[ParsedCard] = chain.invoke(
        {
            "source_text": source_text,
            "key_question": key_question,
            "min_result": max_result,
        }
    )
    return [
        LLMFlashCard(**c, card_type=card_type, topic_id=topic_id) for c in parsed_cards
    ]


def save_llm_flashcards_to_session(
    request: HttpRequest, flashcards: list[LLMFlashCard]
):
    request.session["llm_flashcards"] = [asdict(flashcard) for flashcard in flashcards]


def load_llm_flashcards_from_session(request: HttpRequest) -> list[LLMFlashCard]:
    try:
        return [
            LLMFlashCard(**flashcard) for flashcard in request.session["llm_flashcards"]
        ]
    except KeyError:
        return []


def delete_llm_flashcards_from_session(request: HttpRequest):
    try:
        del request.session["llm_flashcards"]
    except KeyError:
        pass

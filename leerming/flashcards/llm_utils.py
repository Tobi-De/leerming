"""
I'm using anki mark-up because it seem to be the simplest to describe and work with, plus I found an aleady made prompt that 
I can easily adapt to my needs.
The original prompt https://thevitalcurriculum.notion.site/AI-Master-Guides-ca4db7147f3e43f5a92bb297142280f8
"""

import re
import uuid
from dataclasses import dataclass, asdict
from functools import cached_property

from django.http import HttpRequest
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

CLOZED_DELETION_TEMPLATE = """
REVIEW_TEXT: "{source_text}"

FOCUS_ON: "{main_focus_point}"

Task: Your task is to condense the information in the REVIEW_TEXT into concise and direct statements based on the provided FOCUS_ON using Anki cloze deletion mark-up. Ensure that each statement is clearly written, easily understandable, and adheres to the specified formatting and reference criteria. 

Formatting Criteria: 
- Construct a list of pipe "|" separeted string.
- Each string is a a single statement written in Anki cloze deletion mark-up, focusing on the FOCUS_POINT.
- Generate a minimum of {min_result} statements.

Reference Criteria for each "Statement":
- Restrict each statement to 2 cloze deletions. If needed, you may add 1-2 more cloze deletions but restrict them to either cloze1 or cloze2.
- Limit the word count of each statement to less than 40 words.
- Keep the text within the cloze deletions limited to one or two key words.
- Each statement must be able to stand alone. Include the subject of the statement somewhere in the text.
- Each statement must have a least one cloze deletion.
- Keep ONLY simple, direct, cloze deletion statements.
- The statement need to be in the same language as the text to review.

Return only the list of pipe "|" separeted string and strictly nothing else, no words that is not part of the string.

Example:
Sql stands or {{c1::Structured Query Language}} and is used to communicate with databases.|Sql is an {{c1::ANSI}} standard language that is used by all {{c2::relational}} database management systems (RDMS).
"""


@dataclass
class UnsavedFillInTheGapCard:
    id: str
    question: str
    answer: str

    @cached_property
    def split_on_answer(self):
        return self.question.split(self.answer)

    @property
    def before_answer(self):
        return self.split_on_answer[0]

    @property
    def after_answer(self):
        return self.split_on_answer[1]


class PipeSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split("|")


llm = OpenAI()
prompt = PromptTemplate.from_template(CLOZED_DELETION_TEMPLATE)
chain = prompt | llm | PipeSeparatedListOutputParser()


def extract_clozed_deletions(statement):
    cloze_pattern = re.compile(r"{c\d+::(.*?)}")
    cloze_matches = re.findall(cloze_pattern, statement)
    cleaned_statement = re.sub(r"{c\d+::(.*?)}", r"\1", statement)

    return {"statement": cleaned_statement.strip(), "clozed_deletions": cloze_matches}


def make_flashcards_from(source_text: str, main_focus_point: str, max_result: int = 10):
    result = chain.invoke(
        {
            "source_text": source_text,
            "main_focus_point": main_focus_point,
            "min_result": max_result,
        }
    )
    flashcards = []
    for statement in result:
        statement, clozed_deletions = extract_clozed_deletions(statement).values()
        flashcards.extend(
            UnsavedFillInTheGapCard(id=str(uuid.uuid4()), question=statement, answer=cz)
            for cz in clozed_deletions
        )
    return flashcards


def save_tmp_flashcard_to_session(
    request: HttpRequest, flashcards: list[UnsavedFillInTheGapCard]
):
    request.session["tmp_flashcards"] = [asdict(flashcard) for flashcard in flashcards]


def load_tmp_flashcard_from_session(request: HttpRequest):
    try:
        return [
            UnsavedFillInTheGapCard(**flashcard)
            for flashcard in request.session["tmp_flashcards"]
        ]
    except KeyError:
        return []


def delete_tmp_flashcard_from_session(request: HttpRequest):
    try:
        del request.session["tmp_flashcards"]
    except KeyError:
        pass

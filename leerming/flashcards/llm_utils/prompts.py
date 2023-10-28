import re
import uuid
from typing import TypedDict

from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

"""
I'm using anki mark-up because it seem to be the simplest to describe and work with, plus I found an aleady made prompt that
I can easily adapt to my needs.
The original prompt https://thevitalcurriculum.notion.site/AI-Master-Guides-ca4db7147f3e43f5a92bb297142280f8
"""

CLOZED_DELETION_TEMPLATE = """
REVIEW_TEXT: "{source_text}"

KEY_QUESTION: "{key_question}"

TASK: Your task is to condense the information in the REVIEW_TEXT into concise and direct statements based on the provided KEY_QUESTION using Anki cloze deletion mark-up. Ensure that each statement is clearly written, easily understandable, and adheres to the specified formatting and reference criteria.

Formatting Criteria:
- Construct a list of pipe "|" separeted string.
- Each string is a single statement written in Anki cloze deletion mark-up, focusing on one aspect of the KEY_QUESTION.
- Generate a minimum of {min_result} statements.

Reference Criteria for each "Statement":
- Restrict each statement to 2 cloze deletions. If needed, you may add 1-2 more cloze deletions but restrict them to either cloze1 or cloze2.
- Limit the word count of each statement to less than 40 words.
- Keep the text within the cloze deletions limited to one or two key words.
- Each statement must be able to stand alone. Include the subject of the statement somewhere in the text.
- Each statement must have a least one cloze deletion.
- Keep ONLY simple, direct, cloze deletion statements.
- The statement need to be in the same language as the text to review.

Return only the list of pipe "|" separated string and strictly nothing else, no words that is not part of the string.

Example:
Sql stands or {{c1::Structured Query Language}} and is used to communicate with databases.|Sql is an {{c1::ANSI}} standard language that is used by all {{c2::relational}} database management systems (RDMS).
"""

FRONT_BACK_TEMPLATE = """
REVIEW_TEXT: "{source_text}"

KEY_QUESTION: "{key_question}"

TASK: Your task is to convert the REVIEW_TEXT into Basic Note Type (front/back) Anki flashcards. Prioritize information regarding the KEY_QUESTION. Ensure that each flashcard is clearly written, and adheres to the specified formatting and reference criteria.

Formatting Criteria:

- Construct text file with each line of the text being one statement.
- Each statement is a pipe separated question and answer, in the format question|answer.
- Each statement is question|answer focusing on one aspect the KEY_QUESTION.
- The answer should contain the succinct answer to the corresponding question.
- Generate a minimum of {min_result} cards.

Reference Criteria for each "Statement":

- Each statement should test a single concept
- Limit the word count of each question to less than 40 words.
- Each statement MUST be able to stand alone. Include the subject of the flashcard somewhere in the text.
- Keep ONLY simple, direct questions.

Return only text content of statements (each statement on it own line) strictly nothing else.

Example:
what does SQL stand for?|Structured Query Language.
What is sql used for?|Sql is used by all relational database management systems (RDMS).
"""

clozed_delete_template = PromptTemplate.from_template(CLOZED_DELETION_TEMPLATE)
front_back_template = PromptTemplate.from_template(FRONT_BACK_TEMPLATE)


class ParsedCard(TypedDict):
    id: str
    question: str
    answer: str


class PipeSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str) -> list[ParsedCard]:
        """Parse the output of an LLM call."""
        statements = text.strip().split("|")
        flashcards = []
        for statement in statements:
            statement, clozed_deletions = self.extract_clozed_deletions(
                statement
            ).values()
            flashcards.extend(
                {
                    "id": str(uuid.uuid4()),
                    "question": statement,
                    "answer": cz,
                }
                for cz in clozed_deletions
            )
        return flashcards

    @staticmethod
    def extract_clozed_deletions(statement):
        cloze_pattern = re.compile(r"{c\d+::(.*?)}")
        cloze_matches = re.findall(cloze_pattern, statement)
        cleaned_statement = re.sub(r"{c\d+::(.*?)}", r"\1", statement)

        return {
            "statement": cleaned_statement.strip(),
            "clozed_deletions": cloze_matches,
        }


clozed_deletion_output_parser = PipeSeparatedListOutputParser()


class NewLineSeparatedListOutputParser(BaseOutputParser):
    def parse(self, text: str) -> list[ParsedCard]:
        result = text.strip().split("\n")
        flashcards = []
        for qa in result:
            try:
                flashcards.append(
                    {
                        "id": str(uuid.uuid4()),
                        "question": qa.split("|")[0],
                        "answer": qa.split("|")[1],
                    }
                )
            except IndexError:
                continue
        return flashcards


front_back_output_parser = NewLineSeparatedListOutputParser()

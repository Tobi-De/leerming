[![leerming](/leerming/static/logo.png)](https://leerming.com)

> Unlocking Understanding, One Card at a Time

[![fuzzy-couscous](https://img.shields.io/badge/built%20with-fuzzy--couscous-success)](https://github.com/Tobi-De/fuzzy-couscous)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

> [!NOTE]  
> Alpha quality software!.

## Description

Leerming is an open-source Django-based web app that follows the Leitner box method. Create flashcards effortlessly from PDFs, videos, and web links. Supercharge your learning experience.

## Leitner Box Method

The Leitner box method is a simple yet effective technique for learning and retaining information. It works by organizing flashcards into different boxes or levels. As you study, correctly answered flashcards move to higher boxes, while incorrect ones move down. This spaced repetition system helps reinforce your memory over time.

For a more detailed explanation of the Leitner box method, check out [Wikipedia](https://en.wikipedia.org/wiki/Leitner_system).

Certainly, for a technical audience, here's a more detailed and technical version of the sections:

## Leerming Leitner Box Algorithm Implementation

- Flashcards are organized into `NUM_LEVELS` distinct levels. Each card starts at Level 1. The transition between levels is based on performance during reviews.

- Each level corresponds to a specific number of days between reviews as defined by `LEVEL_MAPPING`. For example, Level 1 cards are reviewed daily, while Level 2 cards are reviewed every two days. The exact mapping can be found in the codebase [here](https://github.com/Tobi-De/leerming/blob/f558b7257676f49b352176e7c64b20bd2ffa9d13/leerming/flashcards/models.py#L33).

- During a review, when a card is answered correctly, it moves up to the next level. Once a card reaches Level 7, it is marked as mastered.

- On the other hand, if a card is answered incorrectly during a review, it is downgraded to Level 1, regardless of its previous level. This ensures that challenging material is revisited frequently, while mastered content is reviewed less frequently.

## Card Generation from Documents

Leerming can currently generate flashcards from web pages, YouTube videos, PDF files and Microsoft Word documents.

1. **Text Extraction:** Uploaded documents, regardless of their original format, undergo automated text extraction, transforming the content into a common text format.

2. **Text Segmentation and Storage:** Extracted text is further divided into manageable chunks, which are then embedded and stored in the database using pgvector. This step is executed by a dedicated worker process.

3. **Key Question as Focal Point:** Users provide a key question that serve as a central topic for generating flashcards. Additionally, users select one of their uploaded documents.

4. **Chunk Matching with L2Distance:** Leerming identifies document chunks that are closest to the user's key question using L2Distance, ensuring the relevance of the generated flashcards.

5. **Prompt Generation with Language Models (LLM):** Using the key question and the identified document chunks, Leerming generates an LLM prompt. This prompt is then sent to Language Models (LLM) for card creation.

## Local Development Setup

### Requirements

Ensure you have the following prerequisites in place:

- PostgreSQL database with the [pgvector](https://github.com/pgvector/pgvector) extension. If you use Docker, you can find a suitable [image](https://hub.docker.com/r/ankane/pgvector) available.
- [Rye](https://github.com/mitsuhiko/rye) for streamlined dependency management. While not mandatory, it simplifies the process. You can use the `requirements-dev.lock` in the project root with any tool that supports the Python `requirements.txt` format.
- An openai API key, you can get one at https://platform.openai.com/account/api-keys.

### Setup and Run

Follow these steps to set up and run Leerming locally:

1. Clone the repository: `git clone https://github.com/tobi-de/leerming.git`
2. Navigate to the project directory: `cd leerming`
3. Create and activate a virtual environment: `rye shell`
4. Install dependencies: `rye sync`
5. Create a `.env` file by copying from `.env.template` and fill it out: `cp .env.template .env`
6. Apply migrations: `python manage.py migrate`
7. Create the cache table: `python manage.py createcachetable`
8. Install [Watson](https://github.com/etianen/django-watson) for full-text search: `python manage.py installwatson`
9. Create a superuser: `python manage.py makesuperuser`
10. Start the development server: `python manage.py runserver`

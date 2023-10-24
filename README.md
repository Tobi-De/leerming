# leerming (WIP)

> **Note:** Alpha quality software!.


[![fuzzy-couscous](https://img.shields.io/badge/built%20with-fuzzy--couscous-success)](https://github.com/Tobi-De/fuzzy-couscous)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)


## Description

Leerming is an open-source Django-based web app that follows the Leitner box method. Create flashcards effortlessly from PDFs, videos, and web links. Supercharge your learning experience.

## Leitner Box Method

The Leitner box method is a simple yet effective technique for learning and retaining information. It works by organizing flashcards into different boxes or levels. As you study, correctly answered flashcards move to higher boxes, while incorrect ones move down. This spaced repetition system helps reinforce your memory over time.

For a more detailed explanation of the Leitner box method, check out [Wikipedia](https://en.wikipedia.org/wiki/Leitner_system).

## Local Development Setup

### Requirements

Ensure you have the following prerequisites in place:

- PostgreSQL database with the [pgvector](https://github.com/pgvector/pgvector) extension. If you use Docker, you can find a suitable [image](https://hub.docker.com/r/ankane/pgvector) available.
- [Rye](https://github.com/mitsuhiko/rye) for streamlined dependency management. While not mandatory, it simplifies the process. You can use the `requirements-dev.lock` in the project root with any tool that supports the Python `requirements.txt` format.

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


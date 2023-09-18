# ------------------------------------------------------------
# Base/builder layer
# ------------------------------------------------------------

FROM python:3.11-slim-buster AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.lock /tmp/requirements.txt

# Modify requirements.txt file in a single RUN command
RUN { sed '/-e file/d' /tmp/requirements.txt > /tmp/requirements-modified.txt; mv /tmp/requirements-modified.txt /tmp/requirements.txt; }


# add ",sharing=locked" if release should block until builder is complete
RUN --mount=type=cache,target=/root/.cache,sharing=locked,id=pip \
    pip install --upgrade pip pip-tools && \
    pip install -r /tmp/requirements.txt

# ------------------------------------------------------------
# Dev/testing layer
# ------------------------------------------------------------

FROM builder AS release

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /src/

WORKDIR /src/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ------------------------------------------------------------
# TODO: Add Production notes
# ------------------------------------------------------------

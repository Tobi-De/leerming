FROM python:3.11.0-bullseye as requirements-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /tmp

COPY requirements.lock /tmp/requirements.txt

# Modify requirements.txt file in a single RUN command
RUN { sed '/-e file/d' /tmp/requirements.txt > /tmp/requirements-modified.txt; mv /tmp/requirements-modified.txt /tmp/requirements.txt; }

# add ",sharing=locked" if release should block until builder is complete
#RUN --mount=type=cache,target=/root/.cache,sharing=locked,id=pip \
#    pip install --upgrade pip && \
#    pip install -r /tmp/requirements.txt

FROM python:3.11.0-alpine3.16

WORKDIR /code

RUN apk update \
    && apk add --virtual build-deps build-base \
    && apk add postgresql-client \
    && apk add --no-cache libffi-dev libpq-dev \
    && pip install --upgrade pip \
    && python --version

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 80

CMD ["sh", "/code/docker/entrypoint.sh"]

FROM python:3.10

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

RUN mkdir /app

RUN apt update \
  && apt install -y netcat-traditional \
  && pip3 install --upgrade pip \
  && pip3 install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /app

WORKDIR /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY ./docker-entrypoint.sh /app/docker-entrypoint.sh
COPY . /app

WORKDIR /app

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

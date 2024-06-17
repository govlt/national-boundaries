# Multi stage poetry docker build https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
FROM python:3.12 as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim

# Required for using SpatialLite
RUN apt-get update && apt-get install -y \
  spatialite-bin \
  libsqlite3-mod-spatialite \
  && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    SPATIALITE_LIBRARY_PATH=mod_spatialite.so

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . .

CMD ["fastapi", "run", "main.py", "--port", "80"]

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY pyproject.toml README.md ./
COPY ai_client_configure ./ai_client_configure
COPY sync_service ./sync_service
COPY docs ./docs
COPY tests ./tests
COPY data ./data

RUN pip install --upgrade pip \
    && pip install .[backend]

EXPOSE 8000

CMD ["uvicorn", "sync_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

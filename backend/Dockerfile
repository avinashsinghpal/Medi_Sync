FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install python deps first for better layer caching
COPY pyproject.toml /app/pyproject.toml
COPY medisync /app/medisync

RUN pip install -e ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "medisync.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

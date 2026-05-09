# Self-contained Dockerfile — builds from this project folder only.
# docker build -t atlas-research -f Dockerfile .
FROM python:3.11-slim

WORKDIR /app

# Vendored harness_core (copied into every project for independence)
COPY harness_core ./harness_core
RUN pip install --no-cache-dir -e ./harness_core

COPY pyproject.toml ./pyproject.toml
COPY src ./src
COPY tests ./tests
RUN pip install --no-cache-dir -e '.[dev]'

ENV PYTHONUNBUFFERED=1
EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/healthz', timeout=2)" || exit 1

CMD ["uvicorn", "atlas_research.app:app", "--host", "0.0.0.0", "--port", "8002"]

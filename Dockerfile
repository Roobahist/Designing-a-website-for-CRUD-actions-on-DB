FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY crud_app/ ./crud_app/

RUN python -m pip install --no-cache-dir .

RUN useradd --system --uid 10001 appuser
USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "crud_app.wsgi:app"]

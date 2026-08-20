# GovShield v3.2 — Dockerfile
FROM python:3.11-slim

LABEL maintainer="GovShield Team" \
      description="Ayushman Bharat Fraud Detection System" \
      version="3.2.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project (excluding dev files via .dockerignore)
COPY . .

RUN mkdir -p logs

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:$PORT/api/health || exit 1

CMD ["gunicorn", "wsgi:application", "--config", "gunicorn.conf.py"]

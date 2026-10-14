# ---- Visitor Counter (Flask + Redis) ----
FROM python:3.12-slim

# Build-time metadata passed by the CI pipeline
ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
LABEL org.opencontainers.image.title="visitor-counter" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY wsgi.py .

# Run as a non-root user
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status==200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:app"]

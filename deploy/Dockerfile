FROM python:3.13-slim-bookworm

ARG APP_VERSION=dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_PORT=8000

LABEL org.opencontainers.image.title="诸葛神算 V4" \
      org.opencontainers.image.version="${APP_VERSION}"

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --chown=app:app . .
RUN mkdir -p /app/instance /app/content/articles_en \
    && chown -R app:app /app/instance /app/content

USER 10001:10001

EXPOSE 8000
VOLUME ["/app/instance", "/app/content"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=3)"

CMD ["gunicorn", "--config", "deploy/gunicorn.conf.py", "app:app"]

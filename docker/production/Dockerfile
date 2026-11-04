FROM python:3.12-slim

WORKDIR /app



COPY requirements/ /app/requirements

RUN pip install --no-cache-dir -r /app/requirements/production.txt

COPY . /app/

RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app \
    && mkdir -p /app/data /app/staticfiles /app/media \
    && chmod +x /app/docker/production/entrypoint.sh \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["./docker/production/entrypoint.sh"]

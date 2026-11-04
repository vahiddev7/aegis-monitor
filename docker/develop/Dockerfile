FROM python:3.12-slim

WORKDIR /app



COPY requirements/ /app/requirements

RUN pip install --no-cache-dir -r /app/requirements/develop.txt

COPY . /app/

EXPOSE 8000

RUN chmod +x /app/docker/develop/entrypoint.sh
CMD ["./docker/develop/entrypoint.sh"]

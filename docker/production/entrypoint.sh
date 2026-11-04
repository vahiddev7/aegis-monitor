#!/bin/sh
set -e

echo "Running project ....."

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    python manage.py migrate
fi

if [ "${RUN_COLLECTSTATIC:-true}" = "true" ]; then
    python manage.py collectstatic --noinput
fi

echo "--> Starting web process"
exec gunicorn --bind 0.0.0.0:8000 config.wsgi:application

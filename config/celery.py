import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("aegis")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Periodic task schedule for Aegis health checks
app.conf.beat_schedule = {
    "dispatch-monitors-every-minute": {
        "task": "apps.monitors.tasks.dispatch_active_monitors_task",
        "schedule": 60.0,
    },
}
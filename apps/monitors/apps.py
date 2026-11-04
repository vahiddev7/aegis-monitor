"""AppConfig specification for the monitors domain application."""

from django.apps import AppConfig


class MonitorsConfig(AppConfig):
    """Configuration class for the monitors application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.monitors"
    verbose_name = "Monitors"
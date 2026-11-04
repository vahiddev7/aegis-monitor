"""Database model for alerting targets connected to endpoint monitors."""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.monitors.models.monitor import EndpointMonitor


class NotificationChannel(TimeStampedModel):
    """Destination endpoint configured to receive incident and recovery alerts.

    Attributes:
        monitor (EndpointMonitor): Associated target monitor.
        provider (str): Supported notification provider platform.
        webhook_url (str): Target HTTP endpoint for receiving alert payloads.
        is_active (bool): Operational switch for alert dispatching.
    """

    class Provider(models.TextChoices):
        """Supported notification delivery platforms."""

        DISCORD = "DISCORD", "Discord Webhook"
        TELEGRAM = "TELEGRAM", "Telegram Bot"

    monitor = models.ForeignKey(
        to=EndpointMonitor,
        on_delete=models.CASCADE,
        related_name="notification_channels",
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.DISCORD,
    )
    webhook_url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Notification Channel"
        verbose_name_plural = "Notification Channels"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return identification of the alert channel."""
        return f"{self.monitor.name} -> {self.provider}"
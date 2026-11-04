"""Database model representing monitored HTTP/HTTPS endpoints."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class EndpointMonitor(TimeStampedModel):
    """Represents an external HTTP/HTTPS service endpoint under surveillance.

    Attributes:
        owner (User): The user who owns and configures this monitor.
        name (str): Human-readable identifier for the service.
        url (str): Absolute HTTP or HTTPS target address.
        http_method (str): HTTP request verb (GET, HEAD, POST).
        expected_status_code (int): HTTP response status indicating healthy state.
        interval_seconds (int): Execution frequency between checks in seconds.
        timeout_seconds (int): Maximum wait threshold before timing out.
        is_active (bool): Operational flag enabling or disabling surveillance.
        is_currently_up (bool): Cached health indicator from the latest check.
        last_checked_at (datetime | None): Timestamp of the most recent probe.
    """

    class HTTPMethod(models.TextChoices):
        """Supported HTTP request methods."""

        GET = "GET", "GET"
        HEAD = "HEAD", "HEAD"
        POST = "POST", "POST"

    owner = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monitors",
    )
    name = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    http_method = models.CharField(
        max_length=10,
        choices=HTTPMethod.choices,
        default=HTTPMethod.GET,
    )
    expected_status_code = models.PositiveSmallIntegerField(
        default=200,
        validators=[MinValueValidator(100), MaxValueValidator(599)],
    )
    interval_seconds = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(30), MaxValueValidator(86400)],
        help_text="Check frequency in seconds (minimum 30s).",
    )
    timeout_seconds = models.PositiveSmallIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_currently_up = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Endpoint Monitor"
        verbose_name_plural = "Endpoint Monitors"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "last_checked_at"]),
            models.Index(fields=["owner", "is_currently_up"]),
        ]

    def __str__(self) -> str:
        """Return human-readable monitor identification with health tag."""
        status_label = "UP" if self.is_currently_up else "DOWN"
        return f"{self.name} ({self.url}) - [{status_label}]"
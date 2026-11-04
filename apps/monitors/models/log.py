"""Database model recording health check execution telemetry."""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.monitors.models.monitor import EndpointMonitor


class HealthCheckLog(TimeStampedModel):
    """Immutable audit record storing telemetry for a single health check probe.

    Attributes:
        monitor (EndpointMonitor): The parent target endpoint.
        is_up (bool): Outcome flag indicating if the target met health conditions.
        status_code (int | None): Received HTTP response status code.
        response_time_ms (float | None): Round-trip request latency in milliseconds.
        error_message (str): Diagnostic details in case of connectivity or code failure.
    """

    monitor = models.ForeignKey(
        to=EndpointMonitor,
        on_delete=models.CASCADE,
        related_name="check_logs",
    )
    is_up = models.BooleanField(db_index=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time_ms = models.FloatField(null=True, blank=True)
    error_message = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        verbose_name = "Health Check Log"
        verbose_name_plural = "Health Check Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["monitor", "-created_at"]),
            models.Index(fields=["monitor", "is_up", "-created_at"]),
        ]

    def __str__(self) -> str:
        """Return a compact representation of the probe result."""
        status = "UP" if self.is_up else "DOWN"
        return f"{self.monitor.name} -> {status} ({self.response_time_ms}ms)"
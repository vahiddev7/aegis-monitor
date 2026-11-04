"""Core business logic for creating monitors and probing external endpoints."""

import time
from typing import Any
import httpx
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.monitors.models import EndpointMonitor, HealthCheckLog

User = get_user_model()


def create_endpoint_monitor(
    *,
    owner: Any,
    name: str,
    url: str,
    http_method: str = EndpointMonitor.HTTPMethod.GET,
    expected_status_code: int = 200,
    interval_seconds: int = 60,
    timeout_seconds: int = 10,
) -> EndpointMonitor:
    """Validate and persist a new target endpoint for periodic surveillance.

    Args:
        owner: User instance who owns the monitor.
        name: Identifier name for the target.
        url: Absolute web address to probe.
        http_method: HTTP request verb (GET, HEAD, POST).
        expected_status_code: Target status code indicating health.
        interval_seconds: Frequency in seconds between scheduled checks.
        timeout_seconds: Network connection and read timeout limit.

    Returns:
        EndpointMonitor: The newly created and validated monitor instance.
    """
    monitor = EndpointMonitor(
        owner=owner,
        name=name,
        url=url,
        http_method=http_method,
        expected_status_code=expected_status_code,
        interval_seconds=interval_seconds,
        timeout_seconds=timeout_seconds,
    )
    monitor.full_clean()
    monitor.save()
    return monitor


def execute_health_check(*, monitor: EndpointMonitor) -> HealthCheckLog:
    """Execute an outbound HTTP probe, record metrics, and trigger alerts on status flips.

    Measures latency using high-resolution monotonic timers, records results
    within a database transaction, and schedules notifications if the health
    status changes compared to the prior probe.

    Args:
        monitor: The target EndpointMonitor instance.

    Returns:
        HealthCheckLog: Newly created telemetry log entry.
    """
    start_time = time.perf_counter()
    status_code: int | None = None
    response_time_ms: float | None = None
    error_message: str = ""
    is_up: bool = False

    try:
        with httpx.Client(timeout=monitor.timeout_seconds, follow_redirects=True, trust_env=False) as client:
            response = client.request(method=monitor.http_method, url=monitor.url)
            elapsed_seconds = time.perf_counter() - start_time
            response_time_ms = round(elapsed_seconds * 1000, 2)
            status_code = response.status_code
            is_up = status_code == monitor.expected_status_code

            if not is_up:
                error_message = (
                    f"Unexpected status code: received {status_code}, "
                    f"expected {monitor.expected_status_code}."
                )
    except httpx.TimeoutException:
        elapsed_seconds = time.perf_counter() - start_time
        response_time_ms = round(elapsed_seconds * 1000, 2)
        error_message = f"Request timed out after {monitor.timeout_seconds} seconds."
    except httpx.RequestError as exc:
        error_message = f"Network connection error: {exc.__class__.__name__}."

    previous_status = monitor.is_currently_up
    status_flipped = previous_status != is_up

    with transaction.atomic():
        log_entry = HealthCheckLog.objects.create(
            monitor=monitor,
            is_up=is_up,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )

        monitor.is_currently_up = is_up
        monitor.last_checked_at = timezone.now()
        monitor.save(update_fields=["is_currently_up", "last_checked_at", "updated_at"])

    # Asynchronously dispatch alert task if the endpoint state changed
    if status_flipped:
        from apps.monitors.tasks import send_notifications_task

        send_notifications_task.delay(
            monitor_id=monitor.id,
            is_up=is_up,
            error_message=error_message,
        )

    return log_entry
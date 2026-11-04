"""Celery tasks for scheduled health checks and asynchronous alert dispatching."""

import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from apps.monitors.models import EndpointMonitor, NotificationChannel
from apps.monitors.services.monitor import execute_health_check
from apps.monitors.services.notifications import (
    send_discord_alert,
    send_telegram_alert,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def run_single_monitor_check_task(self, monitor_id: int) -> str:
    """Execute a single health check probe asynchronously within Celery worker.

    Args:
        monitor_id: Primary key ID of the target EndpointMonitor.

    Returns:
        str: Summary string reflecting probe completion.
    """
    try:
        monitor = EndpointMonitor.objects.get(id=monitor_id, is_active=True)
    except ObjectDoesNotExist:
        logger.warning("Monitor with id %s does not exist or is inactive.", monitor_id)
        return f"Monitor {monitor_id} skipped."

    log_entry = execute_health_check(monitor=monitor)
    logger.info(
        "Probe finished for '%s' (ID: %s): status_code=%s, is_up=%s, latency=%sms",
        monitor.name,
        monitor.id,
        log_entry.status_code,
        log_entry.is_up,
        log_entry.response_time_ms,
    )
    return f"Monitor {monitor.id} probed: UP={log_entry.is_up}"


@shared_task
def dispatch_active_monitors_task() -> int:
    """Fan-out probe tasks for all currently active endpoint monitors.

    Intended to be invoked periodically via Celery Beat.
    Queries primary keys only to minimize database payload.

    Returns:
        int: Total number of tasks dispatched to the queue.
    """
    active_monitor_ids = list(
        EndpointMonitor.objects.filter(is_active=True).values_list("id", flat=True)
    )

    for monitor_id in active_monitor_ids:
        run_single_monitor_check_task.delay(monitor_id)

    logger.info("Dispatched health check tasks for %d active monitors.", len(active_monitor_ids))
    return len(active_monitor_ids)


@shared_task
def send_notifications_task(monitor_id: int, is_up: bool, error_message: str) -> int:
    """Deliver outbound alert messages to all active channels linked to a monitor.

    Args:
        monitor_id: Primary key ID of the target EndpointMonitor.
        is_up: Current endpoint health status.
        error_message: Failure diagnostic details if down.

    Returns:
        int: Number of alert notifications successfully dispatched.
    """
    try:
        monitor = EndpointMonitor.objects.get(id=monitor_id)
    except ObjectDoesNotExist:
        logger.error("Cannot dispatch alerts: Monitor %s not found.", monitor_id)
        return 0

    active_channels = monitor.notification_channels.filter(is_active=True)
    dispatched_count = 0

    for channel in active_channels:
        if channel.provider == NotificationChannel.Provider.DISCORD:
            send_discord_alert(
                webhook_url=channel.webhook_url,
                monitor=monitor,
                is_up=is_up,
                error_message=error_message,
            )
            dispatched_count += 1
        elif channel.provider == NotificationChannel.Provider.TELEGRAM:
            send_telegram_alert(
                webhook_url=channel.webhook_url,
                monitor=monitor,
                is_up=is_up,
                error_message=error_message,
            )
            dispatched_count += 1

    logger.info(
        "Dispatched %d notifications for monitor '%s' (State: %s)",
        dispatched_count,
        monitor.name,
        "UP" if is_up else "DOWN",
    )
    return dispatched_count
"""Database selectors and analytical query aggregations for monitors."""

from datetime import timedelta
from typing import Any, TypedDict

from django.db.models import Avg, Count, Q, QuerySet
from django.utils import timezone

from apps.monitors.models import EndpointMonitor, HealthCheckLog


class MonitorMetrics(TypedDict):
    """Structured telemetry metrics over an evaluation time window."""

    total_checks: int
    successful_checks: int
    uptime_percentage: float
    avg_response_time_ms: float


def get_user_monitors(*, user: Any) -> QuerySet[EndpointMonitor]:
    """Retrieve all monitors owned by a specified user.

    Args:
        user: Authenticated user instance.

    Returns:
        QuerySet[EndpointMonitor]: Ordered queryset of owned monitors.
    """
    return EndpointMonitor.objects.filter(owner=user).order_by("-created_at")


def get_monitor_logs(
    *,
    monitor: EndpointMonitor,
    limit: int = 50,
) -> QuerySet[HealthCheckLog]:
    """Retrieve recent health check logs for a given monitor.

    Args:
        monitor: Target EndpointMonitor instance.
        limit: Maximum number of recent log entries to return.

    Returns:
        QuerySet[HealthCheckLog]: Ordered telemetry logs.
    """
    return monitor.check_logs.order_by("-created_at")[:limit]


def calculate_monitor_metrics(
    *,
    monitor: EndpointMonitor,
    hours: int = 24,
) -> MonitorMetrics:
    """Compute uptime ratio and average latency via single SQL aggregation.

    Avoids in-memory iteration over check history by executing conditional
    aggregations directly inside the database engine.

    Args:
        monitor: Target EndpointMonitor instance.
        hours: Evaluation lookback duration in hours.

    Returns:
        MonitorMetrics: Dictionary containing aggregated operational telemetry.
    """
    since_timestamp = timezone.now() - timedelta(hours=hours)

    metrics = monitor.check_logs.filter(created_at__gte=since_timestamp).aggregate(
        total_checks=Count("id"),
        successful_checks=Count("id", filter=Q(is_up=True)),
        avg_latency=Avg("response_time_ms", filter=Q(is_up=True)),
    )

    total = metrics["total_checks"] or 0
    successful = metrics["successful_checks"] or 0
    avg_latency = metrics["avg_latency"] or 0.0

    uptime_pct = round((successful / total) * 100, 2) if total > 0 else 100.0

    return MonitorMetrics(
        total_checks=total,
        successful_checks=successful,
        uptime_percentage=uptime_pct,
        avg_response_time_ms=round(avg_latency, 2),
    )
"""Unit tests verifying mathematical accuracy of monitor telemetry aggregations."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.monitors.models import EndpointMonitor, HealthCheckLog
from apps.monitors.selectors import calculate_monitor_metrics

User = get_user_model()


@pytest.mark.django_db
class TestMonitorMetricsCalculation:
    """Test suite validating aggregated metrics calculation logic."""

    def test_metrics_with_no_logs_returns_default_100_percent(self) -> None:
        """Ensure an endpoint with zero audit logs defaults to 100% uptime."""
        user = User.objects.create_user(username="testuser", password="password123")
        monitor = EndpointMonitor.objects.create(
            owner=user,
            name="Empty Service",
            url="https://empty.example.com",
        )

        metrics = calculate_monitor_metrics(monitor=monitor, hours=24)

        assert metrics["total_checks"] == 0
        assert metrics["successful_checks"] == 0
        assert metrics["uptime_percentage"] == 100.0
        assert metrics["avg_response_time_ms"] == 0.0

    def test_metrics_aggregates_uptime_and_latency_accurately(self) -> None:
        """Verify calculation of mixed healthy/failing logs over lookback window."""
        user = User.objects.create_user(username="testuser2", password="password123")
        monitor = EndpointMonitor.objects.create(
            owner=user,
            name="API Service",
            url="https://api.example.com",
        )

        now = timezone.now()
        # 3 checks: 2 UP (100ms, 200ms) and 1 DOWN (None ms)
        HealthCheckLog.objects.create(
            monitor=monitor, is_up=True, status_code=200, response_time_ms=100.0, created_at=now
        )
        HealthCheckLog.objects.create(
            monitor=monitor, is_up=True, status_code=200, response_time_ms=200.0, created_at=now
        )
        HealthCheckLog.objects.create(
            monitor=monitor, is_up=False, status_code=500, response_time_ms=None, error_message="Internal Error", created_at=now
        )

        metrics = calculate_monitor_metrics(monitor=monitor, hours=24)

        assert metrics["total_checks"] == 3
        assert metrics["successful_checks"] == 2
        # (2 / 3) * 100 = 66.67%
        assert metrics["uptime_percentage"] == 66.67
        # Average of (100.0 + 200.0) / 2 = 150.0ms
        assert metrics["avg_response_time_ms"] == 150.0
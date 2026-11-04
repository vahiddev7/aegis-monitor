"""Integration tests for probe execution and status transition alerting."""

from unittest.mock import patch
import httpx
import pytest
from django.contrib.auth import get_user_model

from apps.monitors.models import EndpointMonitor, HealthCheckLog
from apps.monitors.services import execute_health_check

User = get_user_model()


@pytest.mark.django_db
class TestMonitorHealthCheckService:
    """Test suite validating HTTP probing and state transition mechanics."""

    @pytest.fixture
    def monitor(self) -> EndpointMonitor:
        """Provide a persisted monitor instance configured for GET checks."""
        user = User.objects.create_user(username="monitor_owner", password="password123")
        return EndpointMonitor.objects.create(
            owner=user,
            name="Billing Gateway",
            url="https://billing.example.com/healthz",
            expected_status_code=200,
            is_currently_up=True,
        )

    @patch("apps.monitors.tasks.send_notifications_task.delay")
    @patch("httpx.Client.request")
    def test_successful_probe_records_log_without_alert(
        self, mock_request, mock_notify, monitor: EndpointMonitor
    ) -> None:
        """A healthy 200 response matching current state creates an UP log and triggers no alert."""
        mock_response = httpx.Response(status_code=200, request=httpx.Request("GET", monitor.url))
        mock_request.return_value = mock_response

        log = execute_health_check(monitor=monitor)

        assert log.is_up is True
        assert log.status_code == 200
        assert log.error_message == ""
        assert HealthCheckLog.objects.filter(monitor=monitor).count() == 1

        monitor.refresh_from_db()
        assert monitor.is_currently_up is True
        mock_notify.assert_not_called()

    @patch("apps.monitors.tasks.send_notifications_task.delay")
    @patch("httpx.Client.request")
    def test_state_flip_to_down_dispatches_notification(
        self, mock_request, mock_notify, monitor: EndpointMonitor
    ) -> None:
        """When an UP endpoint returns 500, state flips to DOWN and schedules alerts."""
        mock_response = httpx.Response(status_code=500, request=httpx.Request("GET", monitor.url))
        mock_request.return_value = mock_response

        log = execute_health_check(monitor=monitor)

        assert log.is_up is False
        assert log.status_code == 500
        assert "Unexpected status code" in log.error_message

        monitor.refresh_from_db()
        assert monitor.is_currently_up is False

        # Alert task must be scheduled because previous state was True and now is False
        mock_notify.assert_called_once_with(
            monitor_id=monitor.id,
            is_up=False,
            error_message=log.error_message,
        )

    @patch("apps.monitors.tasks.send_notifications_task.delay")
    @patch("httpx.Client.request")
    def test_timeout_handled_gracefully(
        self, mock_request, mock_notify, monitor: EndpointMonitor
    ) -> None:
        """Timeout exceptions are caught, logged cleanly as DOWN, and trigger alerts."""
        mock_request.side_effect = httpx.TimeoutException("Connection timed out")

        log = execute_health_check(monitor=monitor)

        assert log.is_up is False
        assert log.status_code is None
        assert "timed out" in log.error_message

        monitor.refresh_from_db()
        assert monitor.is_currently_up is False
        mock_notify.assert_called_once()
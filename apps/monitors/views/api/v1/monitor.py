"""API v1 views for managing and inspecting endpoint monitors."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.monitors.models import EndpointMonitor
from apps.monitors.selectors import (
    calculate_monitor_metrics,
    get_monitor_logs,
    get_user_monitors,
)
from apps.monitors.serializers import (
    HealthCheckLogSerializer,
    MonitorInputSerializer,
    MonitorOutputSerializer,
)
from apps.monitors.services import create_endpoint_monitor


class MonitorListCreateAPI(APIView):
    """API endpoint to list owned monitors and register a new endpoint monitor."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Return a collection of monitors owned by the authenticated user.

        Args:
            request: The incoming authenticated request.

        Returns:
            Response: Serialized list of EndpointMonitor records.
        """
        monitors = get_user_monitors(user=request.user)
        data = MonitorOutputSerializer(monitors, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Validate input payload and register a new monitor via service layer.

        Args:
            request: The incoming request containing monitor configuration payload.

        Returns:
            Response: Serialized created EndpointMonitor representation.
        """
        serializer = MonitorInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        monitor = create_endpoint_monitor(
            owner=request.user,
            **serializer.validated_data,
        )
        data = MonitorOutputSerializer(monitor).data
        return Response(data=data, status=status.HTTP_201_CREATED)


class MonitorDetailAPI(APIView):
    """API endpoint to retrieve, inspect or toggle a single monitor."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, monitor_id: int) -> Response:
        """Fetch details of a single monitor owned by the user.

        Args:
            request: The incoming request.
            monitor_id: Target monitor primary key.

        Returns:
            Response: Detailed monitor representation.
        """
        monitor = get_object_or_404(
            EndpointMonitor, id=monitor_id, owner=request.user
        )
        data = MonitorOutputSerializer(monitor).data
        return Response(data=data, status=status.HTTP_200_OK)


class MonitorMetricsAPI(APIView):
    """API endpoint providing aggregated analytics (uptime ratio and average latency)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, monitor_id: int) -> Response:
        """Calculate and return operational metrics for the specified time window.

        Args:
            request: The incoming request with optional 'hours' query parameter.
            monitor_id: Target monitor primary key.

        Returns:
            Response: Telemetry metrics dictionary.
        """
        monitor = get_object_or_404(
            EndpointMonitor, id=monitor_id, owner=request.user
        )
        hours_param = request.query_params.get("hours", "24")
        try:
            hours = int(hours_param)
        except ValueError:
            hours = 24

        metrics = calculate_monitor_metrics(monitor=monitor, hours=hours)
        return Response(data=metrics, status=status.HTTP_200_OK)


class MonitorLogsAPI(APIView):
    """API endpoint returning recent health check probe audit records."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, monitor_id: int) -> Response:
        """Retrieve historical telemetry logs for an endpoint.

        Args:
            request: The incoming request with optional 'limit' query parameter.
            monitor_id: Target monitor primary key.

        Returns:
            Response: List of serialized probe logs.
        """
        monitor = get_object_or_404(
            EndpointMonitor, id=monitor_id, owner=request.user
        )
        limit_param = request.query_params.get("limit", "50")
        try:
            limit = min(int(limit_param), 200)
        except ValueError:
            limit = 50

        logs = get_monitor_logs(monitor=monitor, limit=limit)
        data = HealthCheckLogSerializer(logs, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)
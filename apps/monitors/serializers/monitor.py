"""Serializers for endpoint monitors input validation and representation."""

from rest_framework import serializers

from apps.monitors.models import EndpointMonitor, HealthCheckLog, NotificationChannel


class MonitorInputSerializer(serializers.Serializer):
    """Validates payload required to register a new endpoint monitor."""

    name = serializers.CharField(max_length=120)
    url = serializers.URLField(max_length=500)
    http_method = serializers.ChoiceField(
        choices=EndpointMonitor.HTTPMethod.choices,
        default=EndpointMonitor.HTTPMethod.GET,
    )
    expected_status_code = serializers.IntegerField(
        default=200,
        min_value=100,
        max_value=599,
    )
    interval_seconds = serializers.IntegerField(
        default=60,
        min_value=30,
        max_value=86400,
    )
    timeout_seconds = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=60,
    )


class NotificationChannelSerializer(serializers.ModelSerializer):
    """Serializes notification channels associated with a monitor."""

    class Meta:
        model = NotificationChannel
        fields = [
            "id",
            "provider",
            "webhook_url",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HealthCheckLogSerializer(serializers.ModelSerializer):
    """Serializes audit probe logs for telemetry views."""

    class Meta:
        model = HealthCheckLog
        fields = [
            "id",
            "is_up",
            "status_code",
            "response_time_ms",
            "error_message",
            "created_at",
        ]
        read_only_fields = fields


class MonitorOutputSerializer(serializers.ModelSerializer):
    """Serializes EndpointMonitor instances for API responses."""

    notification_channels = NotificationChannelSerializer(many=True, read_only=True)

    class Meta:
        model = EndpointMonitor
        fields = [
            "id",
            "name",
            "url",
            "http_method",
            "expected_status_code",
            "interval_seconds",
            "timeout_seconds",
            "is_active",
            "is_currently_up",
            "last_checked_at",
            "notification_channels",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
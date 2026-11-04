"""URL routing declarations for the monitors application."""

from django.urls import path

from apps.monitors.views.api.v1 import (
    MonitorDetailAPI,
    MonitorListCreateAPI,
    MonitorLogsAPI,
    MonitorMetricsAPI,
)
from apps.monitors.views.web.dashboard import (
    dashboard_view,
    monitor_create_view,
    monitor_delete_view,
    monitor_trigger_check_view,
    monitor_update_view
)

app_name = "monitors"

urlpatterns = [
    # Web UI Dashboard & Actions
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/create/", monitor_create_view, name="monitor-create"),
    path("dashboard/<int:monitor_id>/update/", monitor_update_view, name="monitor-update"),
    path("dashboard/<int:monitor_id>/trigger/", monitor_trigger_check_view, name="monitor-trigger"),
    path("dashboard/<int:monitor_id>/delete/", monitor_delete_view, name="monitor-delete"),

    # REST APIs v1
    path("", MonitorListCreateAPI.as_view(), name="monitor-list-create"),
    path("<int:monitor_id>/", MonitorDetailAPI.as_view(), name="monitor-detail"),
    path("<int:monitor_id>/metrics/", MonitorMetricsAPI.as_view(), name="monitor-metrics"),
    path("<int:monitor_id>/logs/", MonitorLogsAPI.as_view(), name="monitor-logs"),
]
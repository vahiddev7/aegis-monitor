"""Web presentation views for the Aegis monitoring dashboard."""

from typing import Any
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.monitors.forms import EndpointMonitorForm
from apps.monitors.models import EndpointMonitor, HealthCheckLog
from apps.monitors.selectors import calculate_monitor_metrics, get_user_monitors
from apps.monitors.services import create_endpoint_monitor, execute_health_check


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render the operations dashboard template populated with monitor telemetry."""
    monitors = get_user_monitors(user=request.user)

    total_monitors = monitors.count()
    up_count = monitors.filter(is_currently_up=True).count()
    down_count = total_monitors - up_count

    monitor_cards: list[dict[str, Any]] = []
    total_uptime_sum = 0.0

    for monitor in monitors:
        metrics = calculate_monitor_metrics(monitor=monitor, hours=24)
        monitor_cards.append({
            "monitor": monitor,
            "metrics": metrics,
        })
        total_uptime_sum += metrics["uptime_percentage"]

    overall_uptime = (
        round(total_uptime_sum / total_monitors, 2) if total_monitors > 0 else 100.0
    )

    recent_logs = (
        HealthCheckLog.objects.filter(monitor__owner=request.user)
        .select_related("monitor")
        .order_by("-created_at")[:20]
    )

    form = EndpointMonitorForm()

    context: dict[str, Any] = {
        "total_monitors": total_monitors,
        "up_count": up_count,
        "down_count": down_count,
        "overall_uptime": overall_uptime,
        "monitor_cards": monitor_cards,
        "recent_logs": recent_logs,
        "form": form,
    }

    return render(request, "monitors/dashboard.html", context)


@login_required
def monitor_create_view(request: HttpRequest) -> HttpResponse:
    """Handle creation of a new monitor target via web form."""
    if request.method == "POST":
        form = EndpointMonitorForm(request.POST)
        if form.is_valid():
            create_endpoint_monitor(
                owner=request.user,
                **form.cleaned_data,
            )
            messages.success(request, "Target endpoint added successfully!")
            return redirect("monitors:dashboard")
        else:
            messages.error(request, "Invalid input. Please check the fields.")
    return redirect("monitors:dashboard")


@login_required
def monitor_trigger_check_view(request: HttpRequest, monitor_id: int) -> HttpResponse:
    """Execute an immediate manual health check probe from UI."""
    monitor = get_object_or_404(EndpointMonitor, id=monitor_id, owner=request.user)
    log = execute_health_check(monitor=monitor)

    status_label = "UP" if log.is_up else "DOWN"
    messages.info(
        request,
        f"Probed '{monitor.name}': {status_label} ({log.response_time_ms} ms)",
    )
    return redirect("monitors:dashboard")


@login_required
def monitor_delete_view(request: HttpRequest, monitor_id: int) -> HttpResponse:
    """Delete a target monitor."""
    monitor = get_object_or_404(EndpointMonitor, id=monitor_id, owner=request.user)
    monitor.delete()
    messages.warning(request, f"Target '{monitor.name}' deleted.")
    return redirect("monitors:dashboard")


@login_required
def monitor_update_view(request: HttpRequest, monitor_id: int) -> HttpResponse:
    """Handle editing an existing endpoint monitor."""
    monitor = get_object_or_404(EndpointMonitor, id=monitor_id, owner=request.user)

    if request.method == "POST":
        form = EndpointMonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Target '{monitor.name}' updated successfully.")
            return redirect("monitors:dashboard")
        else:
            messages.error(request, "Failed to update target. Please check the inputs.")
            return redirect("monitors:dashboard")

    # In case of direct GET, redirect back to dashboard
    return redirect("monitors:dashboard")
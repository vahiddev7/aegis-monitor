from django.contrib import admin
from apps.monitors.models import EndpointMonitor, HealthCheckLog, NotificationChannel

@admin.register(EndpointMonitor)
class EndpointMonitorAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "is_currently_up", "is_active", "last_checked_at")

@admin.register(HealthCheckLog)
class HealthCheckLogAdmin(admin.ModelAdmin):
    list_display = ("monitor", "is_up", "status_code", "response_time_ms", "created_at")

@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ("monitor", "provider", "is_active")
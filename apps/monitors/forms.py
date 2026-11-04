"""Web forms for creating and managing endpoint monitors."""

from django import forms
from apps.monitors.models import EndpointMonitor


class EndpointMonitorForm(forms.ModelForm):
    """Form for registering a new endpoint target from the web UI."""

    class Meta:
        model = EndpointMonitor
        fields = [
            "name",
            "url",
            "http_method",
            "expected_status_code",
            "interval_seconds",
            "timeout_seconds",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
                "placeholder": "e.g. Production Billing API",
            }),
            "url": forms.URLInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
                "placeholder": "https://api.example.com/healthz",
            }),
            "http_method": forms.Select(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
            }),
            "expected_status_code": forms.NumberInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
                "min": 100,
                "max": 599,
            }),
            "interval_seconds": forms.NumberInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
                "min": 30,
            }),
            "timeout_seconds": forms.NumberInput(attrs={
                "class": "w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500",
                "min": 1,
                "max": 60,
            }),
        }
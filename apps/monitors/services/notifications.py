"""Outbound notification dispatchers for Discord and Telegram webhooks."""

import logging
import httpx

from apps.monitors.models import EndpointMonitor

logger = logging.getLogger(__name__)


def send_discord_alert(
    *,
    webhook_url: str,
    monitor: EndpointMonitor,
    is_up: bool,
    error_message: str,
) -> None:
    """Dispatch a rich embed incident or recovery alert to a Discord webhook.

    Args:
        webhook_url: Target Discord channel webhook address.
        monitor: The EndpointMonitor instance experiencing state transition.
        is_up: Resulting health state (True for UP, False for DOWN).
        error_message: Diagnostic failure message, if applicable.
    """
    status_label = "RECOVERED (UP)" if is_up else "OUTAGE DETECTED (DOWN)"
    color = 0x2ECC71 if is_up else 0xE74C3C  # Green for UP, Red for DOWN

    payload = {
        "embeds": [
            {
                "title": f"🛡️ Aegis Alert: {monitor.name}",
                "description": f"Endpoint **{monitor.name}** transitioned to **{status_label}**.",
                "color": color,
                "fields": [
                    {"name": "Endpoint URL", "value": f"`{monitor.url}`", "inline": False},
                    {"name": "HTTP Method", "value": monitor.http_method, "inline": True},
                    {
                        "name": "Expected Status",
                        "value": str(monitor.expected_status_code),
                        "inline": True,
                    },
                    {
                        "name": "Details",
                        "value": f"```text\n{error_message or 'Service responding normally.'}\n```",
                        "inline": False,
                    },
                ],
            }
        ]
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(webhook_url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(
            "Failed delivering Discord alert for monitor %s (%s): %s",
            monitor.name,
            monitor.id,
            exc,
        )


def send_telegram_alert(
    *,
    webhook_url: str,
    monitor: EndpointMonitor,
    is_up: bool,
    error_message: str,
) -> None:
    """Send a Markdown-formatted message through Telegram Bot API.

    Args:
        webhook_url: Full Telegram sendMessage endpoint with bot token and chat_id.
        monitor: The EndpointMonitor instance experiencing state transition.
        is_up: Resulting health state (True for UP, False for DOWN).
        error_message: Diagnostic failure message, if applicable.
    """
    icon = "🟢" if is_up else "🔴"
    status_label = "RECOVERED (UP)" if is_up else "OUTAGE DETECTED (DOWN)"

    message = (
        f"{icon} *Aegis Monitor Alert*\n\n"
        f"*Target:* {monitor.name}\n"
        f"*Status:* `{status_label}`\n"
        f"*URL:* `{monitor.url}`\n"
        f"*Details:* `{error_message or 'Service responding normally.'}`"
    )

    payload = {
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(webhook_url, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(
            "Failed delivering Telegram alert for monitor %s (%s): %s",
            monitor.name,
            monitor.id,
            exc,
        )
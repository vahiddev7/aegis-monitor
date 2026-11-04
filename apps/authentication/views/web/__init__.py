"""Expose web authentication views."""

from apps.authentication.views.web.auth import login_view, logout_view

__all__ = [
    "login_view",
    "logout_view",
]
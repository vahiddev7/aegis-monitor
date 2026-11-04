"""Expose authentication views package."""

from apps.authentication.views.web import login_view, logout_view

__all__ = [
    "login_view",
    "logout_view",
]
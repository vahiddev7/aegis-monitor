"""Authentication views for Aegis web interface."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user authentication via standalone dark UI login page."""
    if request.user.is_authenticated:
        return redirect("monitors:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next") or "monitors:dashboard"
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(request, "monitors/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Terminate user session and redirect to login page."""
    logout(request)
    return redirect("monitors:login")
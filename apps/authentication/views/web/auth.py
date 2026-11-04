"""Web authentication views for user session lifecycle."""

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def login_view(request: HttpRequest) -> HttpResponse:
    """Render login UI and authenticate user session.

    Args:
        request: Incoming HTTP request.

    Returns:
        HttpResponse: Rendered login page or redirect to target URL.
    """
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

    return render(request, "authentication/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Terminate authenticated session and redirect to login screen.

    Args:
        request: Incoming HTTP request.

    Returns:
        HttpResponse: Redirect response to login route.
    """
    logout(request)
    return redirect("authentication:login")
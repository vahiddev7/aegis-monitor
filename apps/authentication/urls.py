from django.urls import path

from apps.authentication.views.api.v1.login import LoginView
from apps.authentication.views.api.v1.refresh import RefreshView
from apps.authentication.views.api.v1.register import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # Keep the token endpoint for backwards compatibility.
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
]

import pytest
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.authentication.views.api.v1.login import LoginView
from apps.authentication.views.api.v1.refresh import RefreshView
from apps.authentication.views.api.v1.register import RegisterView
from config.settings import base


class ProtectedTestView(APIView):
    def get(self, request):
        return Response({"ok": True})


def test_drf_requires_authentication_by_default():
    assert base.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == (
        "rest_framework.permissions.IsAuthenticated",
    )


def test_authentication_endpoints_are_explicitly_public():
    assert LoginView.permission_classes == (AllowAny,)
    assert RegisterView.permission_classes == (AllowAny,)
    assert RefreshView.permission_classes == (AllowAny,)


def test_anonymous_request_is_rejected_by_default_permission():
    request = APIRequestFactory().get("/api/protected/")
    response = ProtectedTestView.as_view()(request)

    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_request_passes_default_permission():
    user = get_user_model().objects.create_user(
        username="permission-test-user",
        password="Strong-Test-Password-927!",
    )
    request = APIRequestFactory().get("/api/protected/")
    force_authenticate(request, user=user)
    response = ProtectedTestView.as_view()(request)

    assert response.status_code == 200

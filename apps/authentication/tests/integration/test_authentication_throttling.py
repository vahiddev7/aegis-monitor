import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_is_rate_limited():
    cache.clear()
    client = APIClient()
    payload = {"username": "unknown-user", "password": "invalid-password"}

    responses = [
        client.post("/api/auth/login/", payload, format="json")
        for _ in range(6)
    ]

    assert all(response.status_code == 401 for response in responses[:5])
    assert responses[5].status_code == 429
    cache.clear()


@pytest.mark.django_db
def test_registration_is_rate_limited():
    cache.clear()
    client = APIClient()

    for index in range(3):
        response = client.post(
            "/api/auth/register/",
            {
                "username": f"throttle-user-{index}",
                "email": f"throttle-{index}@example.com",
                "password": "Unique-Strong-Password-927!",
            },
            format="json",
        )
        assert response.status_code == 201

    limited_response = client.post(
        "/api/auth/register/",
        {
            "username": "throttle-user-limited",
            "email": "throttle-limited@example.com",
            "password": "Unique-Strong-Password-927!",
        },
        format="json",
    )

    assert limited_response.status_code == 429
    cache.clear()

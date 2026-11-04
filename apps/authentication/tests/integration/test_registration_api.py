import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_registration_creates_user_without_returning_password():
    response = APIClient().post(
        "/api/auth/register/",
        {
            "username": "registered-user",
            "email": "Registered@Example.com",
            "password": "Unique-Strong-Password-927!",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["username"] == "registered-user"
    assert response.data["email"] == "registered@example.com"
    assert "password" not in response.data
    user = get_user_model().objects.get(username="registered-user")
    assert user.email == "registered@example.com"
    assert user.check_password("Unique-Strong-Password-927!")


@pytest.mark.django_db
def test_registration_rejects_duplicate_username():
    user_model = get_user_model()
    user_model.objects.create_user(
        username="existing-user",
        email="existing@example.com",
        password="Unique-Strong-Password-927!",
    )

    response = APIClient().post(
        "/api/auth/register/",
        {
            "username": "existing-user",
            "email": "another@example.com",
            "password": "Another-Strong-Password-927!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "username" in response.data


@pytest.mark.django_db
def test_registration_rejects_duplicate_email_case_insensitively():
    user_model = get_user_model()
    user_model.objects.create_user(
        username="existing-user",
        email="existing@example.com",
        password="Unique-Strong-Password-927!",
    )

    response = APIClient().post(
        "/api/auth/register/",
        {
            "username": "another-user",
            "email": "Existing@Example.COM",
            "password": "Another-Strong-Password-927!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.data


@pytest.mark.django_db
def test_login_returns_jwt_pair_for_valid_credentials():
    get_user_model().objects.create_user(
        username="login-user",
        email="login@example.com",
        password="Unique-Strong-Password-927!",
    )

    response = APIClient().post(
        "/api/auth/login/",
        {
            "username": "login-user",
            "password": "Unique-Strong-Password-927!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_rejects_invalid_credentials():
    response = APIClient().post(
        "/api/auth/login/",
        {"username": "missing-user", "password": "not-the-password"},
        format="json",
    )

    assert response.status_code == 401

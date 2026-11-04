import pytest
from django.contrib.auth import get_user_model

from apps.authentication.serializers.register import RegisterSerializer


@pytest.mark.django_db
def test_registration_requires_email():
    serializer = RegisterSerializer(
        data={
            "username": "missingemail",
            "password": "Violet-Telescope-94!River",
        }
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_registration_creates_user_with_normalized_email():
    serializer = RegisterSerializer(
        data={
            "username": "registrationtest",
            "email": " Registration@Example.COM ",
            "password": "Violet-Telescope-94!River",
        }
    )

    assert serializer.is_valid(), serializer.errors
    user = serializer.save()

    assert user.email == "registration@example.com"
    assert user.check_password("Violet-Telescope-94!River")


@pytest.mark.django_db
def test_registration_rejects_email_used_with_different_case():
    get_user_model().objects.create_user(
        username="existinguser",
        email="registration@example.com",
        password="Violet-Telescope-94!River",
    )
    serializer = RegisterSerializer(
        data={
            "username": "anotheruser",
            "email": "Registration@Example.com",
            "password": "Violet-Telescope-94!River",
        }
    )

    assert not serializer.is_valid()
    assert "email" in serializer.errors

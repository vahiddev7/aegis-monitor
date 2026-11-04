import pytest
from django.db import IntegrityError, connection, transaction

from apps.users.models import User


@pytest.mark.django_db
def test_user_save_normalizes_email():
    user = User.objects.create_user(
        username="normalized-user",
        email="  Mixed.Case@Example.COM  ",
        password="test-password",
    )

    assert user.email == "mixed.case@example.com"


@pytest.mark.parametrize(
    "email",
    [
        pytest.param(
            "Mixed.Case@example.com",
            marks=pytest.mark.skipif(
                connection.vendor == "microsoft",
                reason=(
                    "The default SQL Server collation is case-insensitive, "
                    "so equality checks cannot detect letter casing."
                ),
            ),
        ),
        " mixed.case@example.com ",
    ],
)
@pytest.mark.django_db
def test_database_rejects_non_normalized_email_updates(email):
    """Sad path: database constraint rejects email values with non-normalized whitespace or casing."""
    user = User.objects.create_user(
        username="database-constraint-user",
        email="canonical@example.com",
        password="test-password",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.filter(pk=user.pk).update(email=email)

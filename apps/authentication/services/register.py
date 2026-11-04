from django.contrib.auth import get_user_model
from django.db import transaction


@transaction.atomic
def register_user(*, username: str, email: str, password: str):
    """Create a user account through the configured user model."""
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

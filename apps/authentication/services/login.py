from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


def authenticate_user(*, username: str, password: str, request=None):
    """Authenticate credentials using Django's configured authentication backends."""
    user = authenticate(request=request, username=username, password=password)
    if user is None:
        raise AuthenticationFailed("Invalid username or password.")
    return user

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_authentication_throttle_cache(db):
    """Keep authentication integration tests independent of throttle history."""
    cache.clear()
    yield
    cache.clear()

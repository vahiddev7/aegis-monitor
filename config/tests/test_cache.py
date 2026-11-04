import pytest
from django.core.cache import cache
from django.conf import settings


def test_default_cache_is_database_backed():
    assert settings.CACHES["default"]["BACKEND"] == (
        "django.core.cache.backends.db.DatabaseCache"
    )
    assert settings.CACHES["default"]["LOCATION"] == "django_cache"


@pytest.mark.django_db
def test_default_cache_supports_shared_cache_operations():
    cache.set("cache-smoke-test", "available", timeout=30)

    assert cache.get("cache-smoke-test") == "available"

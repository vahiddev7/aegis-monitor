from config.settings import base


def test_cross_origin_access_is_restricted_by_default():
    assert base.CORS_ALLOWED_ORIGINS == []
    assert base.CORS_ALLOW_CREDENTIALS is False
    assert base.CSRF_TRUSTED_ORIGINS == []


def test_cors_middleware_runs_before_common_middleware():
    middleware = base.MIDDLEWARE
    assert middleware.index("corsheaders.middleware.CorsMiddleware") < middleware.index(
        "django.middleware.common.CommonMiddleware"
    )

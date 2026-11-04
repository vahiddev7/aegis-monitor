from config.settings import prod


def test_production_security_defaults():
    assert prod.DEBUG is False
    assert prod.SESSION_COOKIE_SECURE is True
    assert prod.CSRF_COOKIE_SECURE is True
    assert prod.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert prod.X_FRAME_OPTIONS == "DENY"
    assert prod.SECURE_REFERRER_POLICY == "strict-origin-when-cross-origin"


def test_https_redirect_and_hsts_are_opt_in_by_default():
    assert prod.SECURE_SSL_REDIRECT is False
    assert prod.SECURE_HSTS_SECONDS == 0
    assert prod.SECURE_HSTS_INCLUDE_SUBDOMAINS is False
    assert prod.SECURE_HSTS_PRELOAD is False
    assert not hasattr(prod, "SECURE_PROXY_SSL_HEADER")

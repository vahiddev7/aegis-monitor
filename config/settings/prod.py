from .base import *

DEBUG = False

# Production browser security defaults. Production deployments must use HTTPS.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Enable HTTPS redirect only when requests reach Django with the correct
# scheme. Behind a TLS-terminating proxy, explicitly trust its forwarded
# protocol header using TRUST_PROXY_SSL_HEADER=True.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
if env.bool("TRUST_PROXY_SSL_HEADER", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS is opt-in until HTTPS is confirmed for every relevant hostname.
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)

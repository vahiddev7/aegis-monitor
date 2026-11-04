import os
import subprocess
import sys


def test_documented_environment_settings_are_applied():
    environment = os.environ.copy()
    environment.update(
        {
            "LANGUAGE_CODE": "en-us",
            "TIME_ZONE": "Europe/Berlin",
            "DEBUG": "False",
        }
    )
    script = """
from config.settings import base, dev, prod

assert base.LANGUAGE_CODE == "en-us"
assert base.TIME_ZONE == "Europe/Berlin"
assert base.STATIC_URL == "/static/"
assert base.MEDIA_URL == "/media/"
assert base.STATIC_ROOT == base.BASE_DIR / "staticfiles"
assert base.MEDIA_ROOT == base.BASE_DIR / "media"
assert dev.DEBUG is False
assert prod.DEBUG is False
"""
    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        env=environment,
    )


def test_development_debug_defaults_to_enabled_without_env_override():
    environment = os.environ.copy()
    environment.pop("DEBUG", None)
    script = """
from config.settings.dev import DEBUG

assert DEBUG is True
"""
    subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        env=environment,
    )

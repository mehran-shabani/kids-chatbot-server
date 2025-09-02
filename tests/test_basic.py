import os
import pytest
from django.conf import settings


def test_timezone_settings():
    assert settings.TIME_ZONE == os.getenv("DJANGO_TIMEZONE", "Asia/Tehran")



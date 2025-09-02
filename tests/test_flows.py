import pytest
from django.utils import timezone


@pytest.mark.django_db
def test_settings_tehran_tz(settings):
    assert settings.TIME_ZONE.endswith("Tehran")



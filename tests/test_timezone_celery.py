def test_timezone_settings(settings):
    assert settings.TIME_ZONE == "Asia/Tehran"
    assert settings.CELERY_TIMEZONE == "Asia/Tehran"
    assert settings.CELERY_ENABLE_UTC is False

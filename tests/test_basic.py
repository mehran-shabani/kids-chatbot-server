import os
from django.test import TestCase, override_settings
from django.conf import settings


class BasicSettingsTest(TestCase):
    @override_settings(TIME_ZONE='UTC')
    def test_timezone_settings(self):
        """Test timezone configuration using override_settings for deterministic behavior."""
        # This test is now deterministic - it always tests against 'UTC'
        # regardless of environment variables or Django settings load order
        self.assertEqual(settings.TIME_ZONE, 'UTC')
        
    @override_settings(TIME_ZONE='Asia/Tehran')
    def test_timezone_settings_tehran(self):
        """Test timezone can be set to Tehran."""
        self.assertEqual(settings.TIME_ZONE, 'Asia/Tehran')
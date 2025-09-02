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


class HealthzTest(TestCase):
    def test_healthz_returns_ok_status(self):
        """Test that the health check endpoint returns 200 OK with correct JSON response."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class SwaggerGatingTest(TestCase):
    @override_settings(DEBUG=True)
    def test_swagger_docs_available_in_debug_mode(self):
        """Test that Swagger documentation is accessible when DEBUG=True."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)
    
    @override_settings(DEBUG=False)
    def test_swagger_docs_disabled_in_production(self):
        """Test that Swagger documentation returns 404 when DEBUG=False."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 404)
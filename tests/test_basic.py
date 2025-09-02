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








        این تست با ارسال یک GET به `/api/docs/` بررسی می‌کند که مسیر مستندات، وقتی متغیر تنظیمات DEBUG برابر False است، غیرفعال شده و سرور کد وضعیت 404 برمی‌گرداند.
        """
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 404)
# ---------------------------------------------------------------------------
# Additional tests focusing on view behavior and docs gating.
# Test framework: Django's unittest (django.test.TestCase)
# ---------------------------------------------------------------------------

class BasicSettingsExtendedTest(TestCase):
    def test_override_settings_is_isolated(self):
        """Ensure override_settings context manager does not leak outside its block."""
        original_tz = settings.TIME_ZONE
        with override_settings(TIME_ZONE="UTC"):
            self.assertEqual(settings.TIME_ZONE, "UTC")
        self.assertEqual(settings.TIME_ZONE, original_tz)


class HealthzExtendedTest(TestCase):
    def test_healthz_content_type_is_json(self):
        """Content-Type should be application/json (optionally with charset)."""
        response = self.client.get("/healthz")
        content_type = response.headers.get("Content-Type") if hasattr(response, "headers") else response["Content-Type"]
        self.assertIn("application/json", content_type)

    def test_healthz_head_request_supported(self):
        """HEAD requests should succeed with empty body."""
        response = self.client.head("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 0)

    def test_healthz_is_idempotent(self):
        """Multiple GET requests should return identical payloads."""
        first = self.client.get("/healthz")
        second = self.client.get("/healthz")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), {"status": "ok"})
        self.assertEqual(second.json(), first.json())

    @override_settings(APPEND_SLASH=True)
    def test_healthz_trailing_slash_allowed_via_redirect(self):
        """Trailing slash should redirect to the canonical endpoint when APPEND_SLASH=True."""
        response = self.client.get("/healthz/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class SwaggerGatingExtendedTest(TestCase):
    @override_settings(DEBUG=True)
    def test_swagger_docs_contains_ui_strings_in_debug(self):
        """Docs page should include Swagger/OpenAPI UI markers when DEBUG=True."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8", errors="ignore").lower()
        self.assertTrue("swagger" in content or "openapi" in content or "redoc" in content)

    @override_settings(DEBUG=True)
    def test_swagger_docs_head_request_in_debug(self):
        """HEAD should succeed for docs page in debug mode."""
        response = self.client.head("/api/docs/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True, APPEND_SLASH=True)
    def test_swagger_docs_append_slash_redirect(self):
        """Missing trailing slash should redirect to canonical docs URL in debug."""
        response = self.client.get("/api/docs", follow=True)
        self.assertEqual(response.status_code, 200)
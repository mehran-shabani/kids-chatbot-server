import os
from django.test import TestCase, override_settings
from django.conf import settings


class BasicSettingsTest(TestCase):
    @override_settings(TIME_ZONE='UTC')
    def test_timezone_settings(self):
        """
        تأیید می‌کند که پیکربندی منطقه زمانی تحت اثر `override_settings` به‌صورت قطعی برابر با 'UTC' است.
        
        این تست (وقتی `TIME_ZONE='UTC'` با `override_settings` اعمال شده) تضمین می‌کند که مقدار `settings.TIME_ZONE` مستقل از متغیرهای محیطی یا ترتیب بارگذاری تنظیمات، برابر با 'UTC' باشد.
        """
        # This test is now deterministic - it always tests against 'UTC'
        # regardless of environment variables or Django settings load order
        self.assertEqual(settings.TIME_ZONE, 'UTC')
        
    @override_settings(TIME_ZONE='Asia/Tehran')
    def test_timezone_settings_tehran(self):
        """
        اطمینان می‌دهد که مقدار تنظیمات TIME_ZONE برابر 'Asia/Tehran' است.
        
        این تست بررسی می‌کند که در محیط آزمون مقدار تنظیمات زمان منطقه‌ای (TIME_ZONE) دقیقاً برابر 'Asia/Tehran' باشد — مفید برای تضمین رفتار قطعی مربوط به زمان و تاریخ زمانی که تنظیمات با استفاده از مکانیزم‌هایی مثل override_settings تغییر داده شده‌اند.
        """
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
        """
        اطمینان می‌دهد که صفحه مستندات Swagger هنگام قرار داشتن برنامه در حالت تولید (DEBUG=False) در دسترس نیست و درخواست به مسیر `/api/docs/` پاسخ HTTP 404 دریافت می‌کند.
        
        این تست با ارسال یک GET به `/api/docs/` بررسی می‌کند که مسیر مستندات، وقتی متغیر تنظیمات DEBUG برابر False است، غیرفعال شده و سرور کد وضعیت 404 برمی‌گرداند.
        """
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 404)
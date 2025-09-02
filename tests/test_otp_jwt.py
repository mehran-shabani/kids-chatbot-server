import os
import pytest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_verify_jwt_flow(client, settings, monkeypatch):
    settings.USE_TZ = True
    settings.TIME_ZONE = "Asia/Tehran"
    settings.REDIS_URL = "redis://localhost:6379/1"

    # Stub Kavenegar
    class DummyAPI:
        def __init__(self, *a, **kw):
            pass

        def verify_lookup(self, *a, **kw):
            return True

    monkeypatch.setitem(os.environ, "KAVEH_NEGAR_API_KEY", "x")

    from accounts import views as acc_views
    acc_views.KavenegarAPI = DummyAPI

    # Fake Redis client for rate limiting
    class FakeRedis:
        store = {}
        def get(self, key):
            return self.store.get(key)
        def setex(self, key, ttl, value):
            self.store[key] = value

    acc_views.r = FakeRedis()

    # Request OTP
    res = client.post("/api/accounts/register-login", {"phone_number": "+989120000000"}, content_type="application/json")
    assert res.status_code == 200

    User = get_user_model()
    u = User.objects.get(phone_number="+989120000000")
    u.auth_code = "123456"
    u.auth_expires_at = timezone.now() + timezone.timedelta(minutes=3)
    u.save()

    res2 = client.post("/api/accounts/verify-otp", {"phone_number": "+989120000000", "code": "123456"}, content_type="application/json")
    assert res2.status_code == 200
    data = res2.json()
    assert "access" in data and "refresh" in data

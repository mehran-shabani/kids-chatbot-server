import random
import logging
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import redis

User = get_user_model()
logger = logging.getLogger(__name__)
r = redis.from_url(settings.REDIS_URL)

OTP_TTL_SECONDS = 180  # 3 دقیقه
RATE_LIMIT_KEY = "otp:lim:"  # otp:lim:<phone>


class RegisterOrLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        if not phone:
            return Response({"error": "Phone number is required."}, status=400)

        # rate limit: 1 پیام در هر 60 ثانیه
        if r.get(f"{RATE_LIMIT_KEY}{phone}"):
            return Response({"error": "لطفاً یک دقیقه بعد دوباره تلاش کنید."}, status=429)
        r.setex(f"{RATE_LIMIT_KEY}{phone}", 60, "1")

        user, _ = User.objects.get_or_create(phone_number=phone, defaults={"username": phone})
        code = f"{random.randint(100000, 999999)}"
        user.auth_code = code
        user.auth_expires_at = timezone.now() + datetime.timedelta(seconds=OTP_TTL_SECONDS)
        user.save(update_fields=["auth_code", "auth_expires_at"])

        try:
            api = KavenegarAPI(settings.KAVEH_NEGAR_API_KEY)
            params = {"receptor": phone, "token": code, "template": settings.KAVEH_NEGAR_TEMPLATE}
            api.verify_lookup(params)
        except (APIException, HTTPException) as e:
            logger.error(f"Kavenegar failed {phone}: {e}")
            return Response({"error": "ارسال کد ناموفق بود."}, status=500)

        return Response({"message": "کد احراز هویت ارسال شد."}, status=200)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")
        if not phone or not code:
            return Response({"message": "شماره و کد الزامی است."}, status=400)
        try:
            u = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response({"message": "کاربر یافت نشد."}, status=404)

        if not u.auth_code or not u.auth_expires_at or timezone.now() > u.auth_expires_at:
            return Response({"message": "کد منقضی شده."}, status=400)
        if str(u.auth_code) != str(code):
            return Response({"message": "کد صحیح نیست."}, status=400)

        # موفق: پاک‌کردن کد و صدور JWT
        u.auth_code = None
        u.auth_expires_at = None
        u.save(update_fields=["auth_code", "auth_expires_at"])

        refresh = RefreshToken.for_user(u)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)}, status=200)


class CompleteProfileView(APIView):
    def post(self, request):
        user = request.user
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        if email:
            user.email = email
        if username:
            user.username = username
        if password:
            user.set_password(password)
        user.save()
        return Response({"message": "پروفایل تکمیل شد."}, status=200)


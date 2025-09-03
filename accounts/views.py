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
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
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


class EmailRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username") or (email or "").split("@")[0]
        password = request.data.get("password")
        role = request.data.get("role")
        if not email or not password:
            return Response({"error": "email و password الزامی است."}, status=400)
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return Response({"error": "کاربری با این ایمیل وجود دارد."}, status=400)
        u = User.objects.create_user(username=username, email=email)
        if role in ("doctor", "patient", "both"):
            u.role = role
        u.set_password(password)
        u.save()
        refresh = RefreshToken.for_user(u)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)}, status=201)


class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"error": "email و password الزامی است."}, status=400)
        User = get_user_model()
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "نام کاربری یا رمز نادرست است."}, status=400)
        # authenticate by username since default backend uses username
        user = authenticate(username=u.username, password=password)
        if not user:
            return Response({"error": "نام کاربری یا رمز نادرست است."}, status=400)
        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)}, status=200)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "email الزامی است."}, status=400)
        User = get_user_model()
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "اگر ایمیل موجود باشد، لینک ارسال می‌شود."}, status=200)
        uidb64 = urlsafe_base64_encode(force_bytes(u.pk))
        token = default_token_generator.make_token(u)
        reset_link = f"{request.build_absolute_uri('/')}reset-password?uid={uidb64}&token={token}"
        try:
            send_mail(
                subject="Password reset",
                message=f"Use this link to reset: {reset_link}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({"uid": uidb64, "token": token}, status=200)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not uidb64 or not token or not new_password:
            return Response({"error": "uid, token, new_password الزامی است."}, status=400)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            User = get_user_model()
            u = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "درخواست نامعتبر."}, status=400)
        if not default_token_generator.check_token(u, token):
            return Response({"error": "توکن نامعتبر است."}, status=400)
        u.set_password(new_password)
        u.save()
        return Response({"message": "رمز عبور تغییر کرد."}, status=200)


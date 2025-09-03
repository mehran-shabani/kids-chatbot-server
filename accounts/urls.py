from django.urls import path
from .views import (
    RegisterOrLoginView,
    VerifyOTPView,
    CompleteProfileView,
    EmailRegisterView,
    EmailLoginView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [
    path("register-login", RegisterOrLoginView.as_view()),
    path("verify-otp", VerifyOTPView.as_view()),
    path("complete-profile", CompleteProfileView.as_view()),
    path("email/register", EmailRegisterView.as_view()),
    path("email/login", EmailLoginView.as_view()),
    path("password/forgot", ForgotPasswordView.as_view()),
    path("password/reset", ResetPasswordView.as_view()),
]


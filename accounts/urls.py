from django.urls import path
from .views import RegisterOrLoginView, VerifyOTPView, CompleteProfileView

urlpatterns = [
    path("register-login", RegisterOrLoginView.as_view()),
    path("verify-otp", VerifyOTPView.as_view()),
    path("complete-profile", CompleteProfileView.as_view()),
]


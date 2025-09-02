from django.urls import path
from .views import ChatSendView, ImageUploadView

urlpatterns = [
    path("send", ChatSendView.as_view()),
    path("image", ImageUploadView.as_view()),
]


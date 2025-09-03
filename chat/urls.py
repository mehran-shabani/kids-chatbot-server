from django.urls import path
from .views import ChatSendView, ImageUploadView, ChatStartView, AgentActionView, ImageProcessView

urlpatterns = [
    path("start", ChatStartView.as_view()),
    path("send", ChatSendView.as_view()),
    path("agent", AgentActionView.as_view()),
    path("image", ImageUploadView.as_view()),
    path("image/process", ImageProcessView.as_view()),
]


from django.urls import path
from .views import ChatSendView

urlpatterns = [
    path("send", ChatSendView.as_view()),
]


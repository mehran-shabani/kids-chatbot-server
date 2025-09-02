from django.urls import path
from .views import WalletView, PurchaseMockView, ModelsListView

urlpatterns = [
    path("wallet", WalletView.as_view()),
    path("purchase", PurchaseMockView.as_view()),
    path("models", ModelsListView.as_view()),
]



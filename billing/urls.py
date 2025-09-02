from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelCatalogViewSet, DevPurchaseMillionView, WalletView

router = DefaultRouter()
router.register("models", ModelCatalogViewSet, basename="models")

urlpatterns = [
    path("", include(router.urls)),
    path("purchase/dev-million/", DevPurchaseMillionView.as_view()),
    path("wallet/", WalletView.as_view()),
]
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from decimal import Decimal
from .models import ModelCatalog, Wallet, Transaction
from .serializers import ModelCatalogSerializer

class ModelCatalogViewSet(ReadOnlyModelViewSet):
    queryset = ModelCatalog.objects.filter(enabled=True)
    serializer_class = ModelCatalogSerializer
    permission_classes = [AllowAny]  # لیست عمومی مشکلی ندارد

class DevPurchaseMillionView(APIView):
    def post(self, request):
        base = Decimal(str(settings.DEFAULT_MILLION_TOKENS_PRICE_USD or 1.0))
        margin = Decimal(str(getattr(settings, "PROFIT_MARGIN", 0.20)))
        price = (base * (1 + margin)).quantize(Decimal("0.01"))
        w, _ = Wallet.objects.get_or_create(user=request.user)
        w.balance_tokens += 1_000_000
        w.save(update_fields=["balance_tokens"])
        Transaction.objects.create(user=request.user, delta_tokens=+1_000_000, reason="topup",
                                   meta={"usd_charged": str(price)})
        return Response({"tokens_added": 1_000_000, "charged_usd": str(price)})

class WalletView(APIView):
    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response({"balance_tokens": wallet.balance_tokens})
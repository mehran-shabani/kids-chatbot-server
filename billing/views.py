from decimal import Decimal
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Wallet, Transaction, ModelCatalog


class WalletView(APIView):
    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response({"balance_tokens": wallet.balance_tokens})


class PurchaseMockView(APIView):
    def post(self, request):
        millions = int(request.data.get("millions", 1))
        base = Decimal(str(settings.DEFAULT_MILLION_TOKENS_PRICE_USD))
        profit = Decimal(str(settings.PROFIT_MARGIN))
        price_usd = (base * millions * (Decimal(1) + profit)).quantize(Decimal("0.01"))
        tokens = millions * 1_000_000
        with transaction.atomic():
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            wallet.balance_tokens += tokens
            wallet.save(update_fields=["balance_tokens"])
            Transaction.objects.create(user=request.user, delta_tokens=tokens, reason="topup", meta={"price_usd": str(price_usd)})
        return Response({"added_tokens": tokens, "price_usd": str(price_usd)})


class ModelsListView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        models = ModelCatalog.objects.filter(enabled=True).values(
            "alias",
            "friendly_name",
            "provider",
            "model_name",
            "input_per_million_usd",
            "output_per_million_usd",
        )
        return Response(list(models))


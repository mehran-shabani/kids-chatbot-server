from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Wallet, Transaction, ModelCatalog
from .pricing import topup_tokens_price_usd


class WalletView(APIView):
    def get(self, request):
        w, _ = Wallet.objects.get_or_create(user=request.user)
        return Response({"balance_tokens": w.balance_tokens}, status=200)


class PurchaseMockView(APIView):
    def post(self, request):
        millions = int(request.data.get("millions", 1))
        tokens_to_add = millions * 1_000_000
        price = str(topup_tokens_price_usd(millions))
        with transaction.atomic():
            w, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
            w.balance_tokens += tokens_to_add
            w.save(update_fields=["balance_tokens"])
            Transaction.objects.create(
                user=request.user,
                delta_tokens=tokens_to_add,
                reason="topup_dev",
                meta={"millions": millions, "price_usd": price},
            )
        return Response({"added": tokens_to_add, "price_usd": price}, status=200)


class ModelsListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        items = [
            {
                "alias": m.alias,
                "friendly_name": m.friendly_name,
                "provider": m.provider,
                "model_name": m.model_name,
                "input_per_million_usd": str(m.input_per_million_usd),
                "output_per_million_usd": str(m.output_per_million_usd),
                "enabled": m.enabled,
            }
            for m in ModelCatalog.objects.filter(enabled=True).order_by("id")
        ]
        return Response(items, status=200)



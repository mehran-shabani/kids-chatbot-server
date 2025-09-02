from decimal import Decimal
from django.db import transaction
from .models import Wallet, ModelCatalog, UsageRecord, Transaction


PROFIT_MARGIN = Decimal("0.20")


def cost_usd(model_alias: str, in_tokens: int, out_tokens: int):
    cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
    usd = (Decimal(in_tokens) / Decimal(1_000_000)) * cat.input_per_million_usd + (
        Decimal(out_tokens) / Decimal(1_000_000)
    ) * cat.output_per_million_usd
    return usd.quantize(Decimal("0.0001"))


@transaction.atomic
def charge_wallet_for_usage(user, model_alias: str, in_tokens: int, out_tokens: int):
    usd = cost_usd(model_alias, in_tokens, out_tokens)
    used_tokens = in_tokens + out_tokens
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
    if wallet.balance_tokens < used_tokens:
        raise ValueError("INSUFFICIENT_WALLET")
    wallet.balance_tokens -= used_tokens
    wallet.save(update_fields=["balance_tokens"])
    Transaction.objects.create(
        user=user,
        delta_tokens=-used_tokens,
        reason="usage",
        meta={"model_alias": model_alias, "usd": str(usd)},
    )
    UsageRecord.objects.create(
        user=user,
        model_alias=model_alias,
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        cost_usd=usd,
    )
    return usd, used_tokens


def topup_tokens_price_usd(millions: int = 1, base_price_per_million_usd: float = 1.0):
    base = Decimal(str(base_price_per_million_usd)) * Decimal(millions)
    return (base * (Decimal(1) + PROFIT_MARGIN)).quantize(Decimal("0.01"))


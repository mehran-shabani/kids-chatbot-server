# billing/pricing.py
from decimal import Decimal
from django.db import transaction
from .models import Wallet, ModelCatalog, UsageRecord, Transaction

def _usd_cost_text(cat, in_tokens: int, out_tokens: int):
    usd = (Decimal(in_tokens)/Decimal(1_000_000))*cat.input_per_million_usd + \
          (Decimal(out_tokens)/Decimal(1_000_000))*cat.output_per_million_usd
    return usd.quantize(Decimal("0.0001"))

def _usd_cost_image(cat, in_reqs: int, out_reqs: int):
    _in  = (cat.per_image_input_usd or Decimal(0))  * Decimal(in_reqs)
    _out = (cat.per_image_output_usd or Decimal(0)) * Decimal(out_reqs)
    return (_in + _out).quantize(Decimal("0.0001"))

def cost_usd(model_alias: str, in_tokens: int, out_tokens: int, *, image_counts=None):
    cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
    if cat.pricing_mode == "text":
        return _usd_cost_text(cat, in_tokens, out_tokens)
    # image mode
    image_counts = image_counts or {"in":1, "out":0}
    return _usd_cost_image(cat, image_counts["in"], image_counts["out"])

@transaction.atomic
def charge_wallet_for_usage(user, model_alias: str, in_tokens: int, out_tokens: int, *, image_counts=None):
    cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
    usd = cost_usd(model_alias, in_tokens, out_tokens, image_counts=image_counts)
    used_tokens = (in_tokens + out_tokens) if cat.pricing_mode=="text" else 1000  # برای تصویر یک عدد ثابت نمادین
    w, _ = Wallet.objects.select_for_update().get_or_create(user=user)
    if w.balance_tokens < used_tokens:
        raise ValueError("INSUFFICIENT_WALLET")
    w.balance_tokens -= used_tokens
    w.save(update_fields=["balance_tokens"])
    Transaction.objects.create(user=user, delta_tokens=-used_tokens, reason="usage",
                               meta={"model_alias":model_alias, "usd":str(usd)})
    UsageRecord.objects.create(user=user, model_alias=model_alias,
                               input_tokens=in_tokens, output_tokens=out_tokens, cost_usd=usd)
    return usd, used_tokens
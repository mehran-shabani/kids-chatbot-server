# billing/management/commands/seed_models.py
from django.core.management.base import BaseCommand
from decimal import Decimal
from billing.models import ModelCatalog

TEXT = [
    # alias, friendly, provider, model_name, input_per_1M, output_per_1M, cached_per_1M(optional)
    ("robot-4o-audio", "چهاراو آدیو", "OpenAI", "gpt-4o-audio-preview", Decimal("2.50"),  Decimal("10.00"), None),
    ("robot-5-mini",   "پنج مینی",   "OpenAI", "gpt-5-mini",            Decimal("0.25"),  Decimal("2.00"),  None),
    ("robot-5",        "پنج",        "OpenAI", "gpt-5",                  Decimal("1.25"),  Decimal("10.00"), None),
    ("robot-4.5-prev", "چهارونیم آزمایشی","OpenAI","gpt-4.5-preview",   Decimal("75.00"), Decimal("150.00"), Decimal("37.50")),
    ("robot-4o-chat",  "چهاراو چت",  "OpenAI", "chatgpt-4o-latest",     Decimal("5.00"),  Decimal("15.00"), None),
    ("robot-o3h",      "او۳ مینی های", "OpenAI","o3-mini-high",         Decimal("1.10"),  Decimal("4.40"),  None),
    ("robot-4.1-mini", "۴.۱ مینی",   "OpenAI", "gpt-4.1-mini",          Decimal("0.40"),  Decimal("1.60"),  Decimal("0.10")),
    ("robot-4o",       "چهاراو",     "OpenAI", "gpt-4o",                Decimal("2.50"),  Decimal("10.00"), None),
    ("robot-5-chat",   "۵ چت لِیتست","OpenAI", "gpt-5-chat-latest",     Decimal("1.25"),  Decimal("10.00"), None),
]

IMAGES = [
    # alias, friendly, provider, model_name, per_image_input, per_image_output
    ("painter-dalle3", "نقاش۳", "OpenAI", "dall-e-3",     Decimal("0.040"), None),
    ("painter-gpti1",  "تصویرگر", "OpenAI", "gpt-image-1", Decimal("10.00"), Decimal("40.00")),
    ("painter-dalle2", "نقاش۲", "OpenAI", "dall-e-2",     Decimal("0.018"), None),
]

class Command(BaseCommand):
    help = "Seed ModelCatalog with pricing (text/image)."

    def handle(self, *args, **kwargs):
        for a, fr, prov, name, pin, pout, pc in TEXT:
            ModelCatalog.objects.update_or_create(
                alias=a, defaults=dict(
                    friendly_name=fr, provider=prov, model_name=name,
                    pricing_mode="text",
                    input_per_million_usd=pin, output_per_million_usd=pout,
                    cached_per_million_usd=pc, enabled=True
                )
            )
        for a, fr, prov, name, per_in, per_out in IMAGES:
            ModelCatalog.objects.update_or_create(
                alias=a, defaults=dict(
                    friendly_name=fr, provider=prov, model_name=name,
                    pricing_mode="image",
                    per_image_input_usd=per_in, per_image_output_usd=per_out,
                    enabled=True
                )
            )
        self.stdout.write(self.style.SUCCESS("ModelCatalog seeded."))
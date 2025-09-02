from decimal import Decimal
from django.core.management.base import BaseCommand
from billing.models import ModelCatalog


SEEDS = [
    {
        "alias": "robot-nano",
        "friendly_name": "ربات نانو",
        "provider": "OpenAI",
        "model_name": "gpt-5-nano",
        "input_per_million_usd": Decimal("0.050"),
        "output_per_million_usd": Decimal("0.400"),
    },
    {
        "alias": "robot-4o-mini",
        "friendly_name": "ربات 4o مینی",
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "input_per_million_usd": Decimal("0.150"),
        "output_per_million_usd": Decimal("0.600"),
    },
    {
        "alias": "robot-4.1",
        "friendly_name": "ربات 4.1",
        "provider": "OpenAI",
        "model_name": "gpt-4.1",
        "input_per_million_usd": Decimal("2.000"),
        "output_per_million_usd": Decimal("8.000"),
    },
    {
        "alias": "robot-image",
        "friendly_name": "ربات تصویر",
        "provider": "OpenAI",
        "model_name": "gpt-image-1",
        "input_per_million_usd": Decimal("10.000"),
        "output_per_million_usd": Decimal("40.000"),
    },
]


class Command(BaseCommand):
    help = "Seed initial ModelCatalog records"

    def handle(self, *args, **options):
        for item in SEEDS:
            obj, created = ModelCatalog.objects.update_or_create(
                alias=item["alias"],
                defaults=item,
            )
            self.stdout.write(self.style.SUCCESS(f"Seeded {obj.alias} ({'created' if created else 'updated'})"))

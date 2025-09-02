from django.core.management.base import BaseCommand
from billing.models import ModelCatalog
from decimal import Decimal


SEEDS = [
    {
        "alias": "robot-nano",
        "friendly_name": "Robot Nano",
        "provider": "OpenAI",
        "model_name": "gpt-5-nano",
        "input_per_million_usd": Decimal("0.050"),
        "output_per_million_usd": Decimal("0.400"),
    },
    {
        "alias": "robot-4o-mini",
        "friendly_name": "Robot 4o Mini",
        "provider": "OpenAI",
        "model_name": "gpt-4o-mini",
        "input_per_million_usd": Decimal("0.150"),
        "output_per_million_usd": Decimal("0.600"),
    },
    {
        "alias": "robot-4.1",
        "friendly_name": "Robot 4.1",
        "provider": "OpenAI",
        "model_name": "gpt-4.1",
        "input_per_million_usd": Decimal("2.000"),
        "output_per_million_usd": Decimal("8.000"),
    },
    {
        "alias": "robot-image",
        "friendly_name": "Robot Image",
        "provider": "OpenAI",
        "model_name": "gpt-image-1",
        "input_per_million_usd": Decimal("10.000"),
        "output_per_million_usd": Decimal("40.000"),
    },
]


class Command(BaseCommand):
    help = "Seed model catalog with default kids-friendly aliases"

    def handle(self, *args, **options):
        created = 0
        for item in SEEDS:
            obj, was_created = ModelCatalog.objects.update_or_create(
                alias=item["alias"],
                defaults={
                    "friendly_name": item["friendly_name"],
                    "provider": item["provider"],
                    "model_name": item["model_name"],
                    "input_per_million_usd": item["input_per_million_usd"],
                    "output_per_million_usd": item["output_per_million_usd"],
                    "enabled": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new models (upserted)."))



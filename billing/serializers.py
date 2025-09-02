from rest_framework import serializers
from .models import ModelCatalog


class ModelCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCatalog
        fields = (
            "alias",
            "friendly_name",
            "provider",
            "model_name",
            "input_per_million_usd",
            "output_per_million_usd",
            "enabled",
        )



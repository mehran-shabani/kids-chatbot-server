from rest_framework import serializers
from .models import ModelCatalog

class ModelCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelCatalog
        fields = ("alias","friendly_name","provider","model_name","pricing_mode",
                  "input_per_million_usd","output_per_million_usd","cached_per_million_usd",
                  "per_image_input_usd","per_image_output_usd","enabled")
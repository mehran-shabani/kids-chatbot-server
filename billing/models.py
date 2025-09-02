from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance_tokens = models.BigIntegerField(default=0)


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delta_tokens = models.BigIntegerField()
    reason = models.CharField(max_length=64)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tokens_per_month = models.BigIntegerField(default=1_000_000)
    active = models.BooleanField(default=True)
    renew_day = models.PositiveSmallIntegerField(default=1)


PRICING_MODES = (("text", "text"), ("image", "image"))


class ModelCatalog(models.Model):
    # alias برای نمایش کودکانه و انتخاب در کلاینت
    alias = models.CharField(max_length=64, unique=True)
    friendly_name = models.CharField(max_length=128, default="")
    provider = models.CharField(max_length=32, default="OpenAI")
    model_name = models.CharField(max_length=128)
    pricing_mode = models.CharField(max_length=8, choices=PRICING_MODES, default="text")
    # قیمت‌های متن (USD per 1M tokens):
    input_per_million_usd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    output_per_million_usd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    cached_per_million_usd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    # قیمت‌های تصویر (USD per request):
    per_image_input_usd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    per_image_output_usd = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    enabled = models.BooleanField(default=True)


class UsageRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    model_alias = models.CharField(max_length=64)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


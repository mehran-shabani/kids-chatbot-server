from django.contrib import admin
from .models import Wallet, Transaction, Subscription, ModelCatalog, UsageRecord


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance_tokens")
    search_fields = ("user__username", "user__phone_number")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "delta_tokens", "reason", "created_at")
    list_filter = ("reason",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tokens_per_month", "active", "renew_day")


@admin.register(ModelCatalog)
class ModelCatalogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "alias",
        "friendly_name",
        "provider",
        "model_name",
        "input_per_million_usd",
        "output_per_million_usd",
        "enabled",
    )
    list_filter = ("enabled", "provider")
    search_fields = ("alias", "friendly_name", "model_name")


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model_alias", "input_tokens", "output_tokens", "cost_usd", "created_at")
    list_filter = ("model_alias",)

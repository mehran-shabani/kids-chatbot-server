import pytest
from django.contrib.auth import get_user_model
from billing.models import Wallet, ModelCatalog


@pytest.mark.django_db
def test_chat_deducts_wallet(client, settings, monkeypatch):
    settings.REDIS_URL = "redis://localhost:6379/1"

    # Seed a model
    ModelCatalog.objects.create(
        alias="robot-4o-mini",
        friendly_name="ربات 4o مینی",
        provider="OpenAI",
        model_name="gpt-4o-mini",
        input_per_million_usd=0.150,
        output_per_million_usd=0.600,
        enabled=True,
    )

    # Stub OpenAI client usage
    class DummyResp:
        class Usage:
            prompt_tokens = 100
            completion_tokens = 200

        class Choice:
            class Message:
                content = "hello"

            message = Message()

        usage = Usage()
        choices = [Choice()]

    from chat import openai_client

    def dummy_chat_completion(model, messages, tools=None):
        return DummyResp(), (100, 200)

    openai_client.chat_completion = dummy_chat_completion

    User = get_user_model()
    u = User.objects.create_user(username="u1")
    wallet, _ = Wallet.objects.get_or_create(user=u)
    wallet.balance_tokens = 1_000_000
    wallet.save()

    # Authenticate by force
    client.force_login(u)
    res = client.post(
        "/api/chat/send",
        {"model_alias": "robot-4o-mini", "prompt": "hi"},
        content_type="application/json",
    )
    assert res.status_code == 200
    wallet.refresh_from_db()
    # 100 + 200 tokens deducted
    assert wallet.balance_tokens == 1_000_000 - 300

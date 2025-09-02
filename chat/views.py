from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .openai_client import chat_completion
from billing.pricing import charge_wallet_for_usage
from billing.models import ModelCatalog
from .models import ChatThread, ChatMessage, MemorySummary


def build_messages_with_memory(thread: ChatThread, user_msg: str):
    last_summary = MemorySummary.objects.filter(thread=thread).order_by("-id").first()
    system_prompt = last_summary.summary if last_summary else "You are a kind assistant for kids."
    msgs = [{"role": "system", "content": system_prompt}]
    for m in ChatMessage.objects.filter(thread=thread).order_by("id")[-10:]:
        msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": user_msg})
    return msgs


class ChatSendView(APIView):
    def post(self, request):
        model_alias = request.data.get("model_alias")
        prompt = request.data.get("prompt")
        thread_id = request.data.get("thread_id")

        if not prompt or not model_alias:
            return Response({"error": "prompt and model_alias required"}, status=400)

        try:
            cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
        except ModelCatalog.DoesNotExist:
            return Response({"error": "invalid model alias"}, status=400)

        if thread_id:
            try:
                thread = ChatThread.objects.get(id=thread_id, user=request.user)
            except ChatThread.DoesNotExist:
                return Response({"error": "thread not found"}, status=404)
        else:
            thread = ChatThread.objects.create(user=request.user, model_alias=model_alias)

        messages = build_messages_with_memory(thread, prompt)
        resp, (in_tokens, out_tokens) = chat_completion(cat.model_name, messages, tools=None)

        text = getattr(resp.choices[0].message, "content", "")
        with transaction.atomic():
            ChatMessage.objects.create(thread=thread, role="user", content=prompt, tokens_in=in_tokens)
            ChatMessage.objects.create(thread=thread, role="assistant", content=text, tokens_out=out_tokens)
            try:
                charge_wallet_for_usage(request.user, model_alias, in_tokens, out_tokens)
            except ValueError as e:
                if str(e) == "INSUFFICIENT_WALLET":
                    return Response({"error": "Insufficient wallet"}, status=402)
                raise

        return Response(
            {
                "thread_id": str(thread.id),
                "reply": text,
                "usage": {"prompt_tokens": in_tokens, "completion_tokens": out_tokens},
            },
            status=200,
        )



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from . import openai_client
from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import UploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from billing.pricing import charge_wallet_for_usage
from billing.models import ModelCatalog
from .models import ChatThread, ChatMessage, MemorySummary, ImageTask


def build_messages_with_memory(thread: ChatThread, user_msg: str):
    msgs = [
        {
            "role": "system",
            "content": (
                MemorySummary.objects.filter(thread=thread).order_by("-id").first()
                or MemorySummary(summary="")
            ).summary
            or "You are a kind assistant for kids.",
        }
    ]
    recent_msgs = ChatMessage.objects.filter(thread=thread).order_by("-id")[:10]
    for m in reversed(list(recent_msgs)):
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
        resp, (in_tokens, out_tokens) = openai_client.chat_completion(cat.model_name, messages, tools=None)

        choice = resp.choices[0]
        text = getattr(choice.message, "content", "") if hasattr(choice, "message") else ""

        try:
            with transaction.atomic():
                ChatMessage.objects.create(thread=thread, role="user", content=prompt, tokens_in=in_tokens)
                ChatMessage.objects.create(thread=thread, role="assistant", content=text, tokens_out=out_tokens)
                charge_wallet_for_usage(request.user, model_alias, in_tokens, out_tokens)
        except ValueError as e:
            if str(e) == "INSUFFICIENT_WALLET":
                return Response({"error": "insufficient wallet"}, status=402)
            raise

        return Response(
            {
                "thread_id": str(thread.id),
                "reply": text,
                "usage": {"prompt_tokens": in_tokens, "completion_tokens": out_tokens},
            },
            status=200,
        )


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file: UploadedFile | None = request.FILES.get("image")
        model_alias = request.data.get("model_alias")
        prompt = request.data.get("prompt", "")
        if not file or not model_alias:
            return Response({"error": "image and model_alias required"}, status=400)

        # ensure bucket
        endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
        secure = settings.MINIO_ENDPOINT.startswith("https://")
        client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=secure,
        )
        bucket = settings.MINIO_BUCKET
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)

        # store file
        object_name = f"uploads/{file.name}"
        client.put_object(bucket, object_name, file, length=file.size, content_type=file.content_type)

        # For now, just echo location (hook to OpenAI image APIs can be added)
        url = f"{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"
        return Response({"image_url": url, "model_alias": model_alias, "prompt": prompt}, status=200)


class ChatStartView(APIView):
    def post(self, request):
        model_alias = request.data.get("model_alias")
        title = request.data.get("title", "")
        if not model_alias:
            return Response({"error": "model_alias required"}, status=400)
        try:
            cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
        except ModelCatalog.DoesNotExist:
            return Response({"error": "invalid model alias"}, status=400)
        thread = ChatThread.objects.create(user=request.user, model_alias=model_alias, title=title)
        return Response({"thread_id": thread.id, "model_name": cat.model_name}, status=201)


class AgentActionView(APIView):
    def post(self, request):
        action = request.data.get("action")
        thread_id = request.data.get("thread_id")
        if action not in ("summarize",):
            return Response({"error": "invalid action"}, status=400)
        try:
            thread = ChatThread.objects.get(id=thread_id, user=request.user)
        except ChatThread.DoesNotExist:
            return Response({"error": "thread not found"}, status=404)
        msgs = ChatMessage.objects.filter(thread=thread).order_by("id")
        text = "\n".join(f"{m.role[:1]}: {m.content}" for m in msgs[max(0, msgs.count()-10):])
        MemorySummary.objects.create(thread=thread, summary=f"Condensed: {text[:800]}")
        return Response({"message": "summary created"}, status=200)


class ImageProcessView(APIView):
    def post(self, request):
        model_alias = request.data.get("model_alias")
        prompt = request.data.get("prompt", "")
        object_name = request.data.get("object_name")
        if not model_alias or not object_name:
            return Response({"error": "model_alias and object_name required"}, status=400)
        try:
            cat = ModelCatalog.objects.get(alias=model_alias, enabled=True)
        except ModelCatalog.DoesNotExist:
            return Response({"error": "invalid model alias"}, status=400)
        task = ImageTask.objects.create(user=request.user, model_alias=model_alias, prompt=prompt, object_name=object_name)
        # For OpenAI image: use prompt only; for future vision, extend to pass image URL
        try:
            resp = openai_client.generate_image(cat.model_name, prompt or f"Enhance image: {object_name}")
            task.result = {"response": getattr(resp, "data", None) or str(resp)}
            task.status = "completed"
            task.save(update_fields=["result", "status"])
            # charge nominal image usage
            charge_wallet_for_usage(request.user, model_alias, 0, 0, image_counts={"in":1, "out":1})
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            task.save(update_fields=["result", "status"])
            return Response({"error": "processing failed"}, status=500)
        return Response({"task_id": task.id, "status": task.status, "result": task.result}, status=200)


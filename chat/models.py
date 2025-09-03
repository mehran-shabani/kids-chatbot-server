from django.db import models
from django.conf import settings


class ChatThread(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default="")
    model_alias = models.CharField(max_length=64)
    memory_summary = models.TextField(blank=True, default="")
    last_activity = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    role = models.CharField(max_length=16)
    content = models.TextField()
    tokens_in = models.IntegerField(default=0)
    tokens_out = models.IntegerField(default=0)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MemorySummary(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    summary = models.TextField()
    up_to_message_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ImageTask(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("completed", "completed"),
        ("failed", "failed"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    model_alias = models.CharField(max_length=64)
    prompt = models.TextField(blank=True, default="")
    object_name = models.CharField(max_length=255)
    result = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)


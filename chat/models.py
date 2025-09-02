from django.db import models
from django.conf import settings


class ChatThread(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default="")
    model_alias = models.CharField(max_length=64)
    last_activity = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    tokens_in = models.IntegerField(default=0)
    tokens_out = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(default=dict, blank=True)


class MemorySummary(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    summary = models.TextField()
    up_to_message_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



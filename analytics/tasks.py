from celery import shared_task
from chat.models import ChatThread, ChatMessage, MemorySummary


@shared_task
def summarize_active_threads():
    for t in ChatThread.objects.all():
        msgs = ChatMessage.objects.filter(thread=t).order_by("-id")[:30]
        if not msgs:
            continue
        txt = "\n".join(f"{m.role[:1]}: {m.content[:100]}" for m in msgs[::-1])
        MemorySummary.objects.create(thread=t, summary=f"Condensed: {txt[:800]}")



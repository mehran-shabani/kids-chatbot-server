from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache


@require_http_methods(["GET", "HEAD"])
@never_cache
def healthz(request):
    """
    بررسی سلامت سادهٔ سرویس؛ پاسخ JSON {"status": "ok"} را با وضعیت HTTP 200 بازمی‌گرداند.
    
    این view برای استفاده به‌عنوان health check در محیط‌هایی مانند Docker یا Kubernetes طراحی شده است. فقط درخواست‌های GET باید به این endpoint فرستاده شوند و پاسخ قابل cache نیست (با استفاده از دکوریتورهای مربوطه در سطح ماژول/ویو). پاسخ از نوع application/json است و مقدار بدنه برای نشان دادن سلامت سرویس برابر با {"status": "ok"} است.
    """
    return JsonResponse({"status": "ok"})
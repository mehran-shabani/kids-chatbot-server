from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache


@require_GET
@never_cache
def healthz(request):
    """Simple health check endpoint for Docker/Kubernetes."""
    return JsonResponse({"status": "ok"})
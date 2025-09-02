from django.http import JsonResponse


def healthz(request):
    """Simple health check endpoint for Docker/Kubernetes."""
    return JsonResponse({"status": "ok"})
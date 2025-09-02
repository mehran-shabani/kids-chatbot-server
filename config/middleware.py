import json
import logging
import time


logger = logging.getLogger("audit")


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        user_id = getattr(getattr(request, "user", None), "id", None)
        path = request.path
        method = request.method
        ip = request.META.get("REMOTE_ADDR")
        try:
            response = self.get_response(request)
            status = getattr(response, "status_code", 0)
            duration_ms = int((time.time() - start) * 1000)
            payload = {
                "event": "http_request",
                "path": path,
                "method": method,
                "status": status,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "ip": ip,
            }
            logger.info(json.dumps(payload, ensure_ascii=False))
            return response
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            payload = {
                "event": "http_exception",
                "path": path,
                "method": method,
                "duration_ms": duration_ms,
                "user_id": user_id,
                "ip": ip,
                "error": str(e),
            }
            logger.exception(json.dumps(payload, ensure_ascii=False))
            raise

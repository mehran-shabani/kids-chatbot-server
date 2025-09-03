from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponseNotFound
from billing.views import ModelsListView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .health import healthz
from chat.views import ImageUploadView, ImageProcessView

def _debug_only(view):
    def _inner(request, *args, **kwargs):
        if not settings.DEBUG:
            return HttpResponseNotFound()
        return view(request, *args, **kwargs)
    return _inner


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz_no_slash"),
    path("healthz/", healthz, name="healthz"),
    path("api/accounts/", include("accounts.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/billing/", include("billing.urls")),
    path("api/models", ModelsListView.as_view()),
    # Image API short paths
    path("api/image/upload", ImageUploadView.as_view()),
    path("api/image/process", ImageProcessView.as_view()),
    # Swagger/Schema (gated at request-time)
    path("api/schema/", _debug_only(SpectacularAPIView.as_view()), name="schema"),
    path("api/docs/", _debug_only(SpectacularSwaggerView.as_view(url_name="schema")), name="swagger-ui"),
]



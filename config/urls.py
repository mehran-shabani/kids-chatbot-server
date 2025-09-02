from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from billing.views import ModelsListView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .health import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("api/accounts/", include("accounts.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/billing/", include("billing.urls")),
    path("api/models", ModelsListView.as_view()),
]

# Add Swagger/Schema views only in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.accounts.views import HomeRedirectView

urlpatterns = [
   
    path("", HomeRedirectView.as_view(), name="home"),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon/favicon.ico", permanent=True),
        name="favicon",
    ),

    path("django-admin/", admin.site.urls),
    path("auth/", include("apps.accounts.urls", namespace="accounts")),
    path("applications/", include("apps.applications.urls", namespace="applications")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
    path("reviews/", include("apps.reviews.urls", namespace="reviews")),
    path("audit/", include("apps.audit.urls", namespace="audit")),
    path("visas/", include("apps.visas.urls", namespace="visas")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

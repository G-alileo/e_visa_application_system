from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("auth/", include("apps.accounts.urls", namespace="accounts")),
    path("applications/", include("apps.applications.urls", namespace="applications")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
    path("reviews/", include("apps.reviews.urls", namespace="reviews")),
    path("audit/", include("apps.audit.urls", namespace="audit")),
    path("visas/", include("apps.visas.urls", namespace="visas")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

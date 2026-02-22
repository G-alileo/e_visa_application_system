from django.urls import path

from apps.applications.views import (
    ApplicantDashboardView,
    ApplicationStatusView,
    CreateApplicationView,
    ReApplicationView,
    RecommendationsView,
    SubmitApplicationView,
    UploadDocumentsView,
)

app_name = "applications"

urlpatterns = [
    path("dashboard/", ApplicantDashboardView.as_view(), name="dashboard"),
    path("new/", CreateApplicationView.as_view(), name="create"),
    path("<uuid:pk>/", ApplicationStatusView.as_view(), name="status"),
    path("<uuid:pk>/upload/", UploadDocumentsView.as_view(), name="upload"),
    path("<uuid:pk>/submit/", SubmitApplicationView.as_view(), name="submit"),
    path("<uuid:pk>/recommendations/", RecommendationsView.as_view(), name="recommendations"),
    path("<uuid:pk>/re-apply/", ReApplicationView.as_view(), name="re_apply"),
]

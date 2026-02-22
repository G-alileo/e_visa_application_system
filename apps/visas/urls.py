from django.urls import path

from apps.visas.views import (
    SupervisorOverrideView,
    SystemReportsView,
    VisaTypeManagementView,
    VisaTypeToggleView,
)

app_name = "visas"

urlpatterns = [
    path("supervisor/override/", SupervisorOverrideView.as_view(), name="supervisor_override"),
    path("admin/types/", VisaTypeManagementView.as_view(), name="visa_types"),
    path("admin/types/<int:pk>/toggle/", VisaTypeToggleView.as_view(), name="toggle_visa_type"),
    path("admin/reports/", SystemReportsView.as_view(), name="reports"),
]

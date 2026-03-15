from django.urls import path

from apps.visas.views import (
    ApplicationInterviewsView,
    ApplicantInterviewsView,
    CancelInterviewView,
    IssueVisaView,
    MarkInterviewCompletedView,
    ScheduleInterviewView,
    SupervisorOverrideView,
    SystemReportsView,
    VisaDownloadFileView,
    VisaDownloadPageView,
    VisaTypeManagementView,
    VisaTypeToggleView,
)

app_name = "visas"

urlpatterns = [
    # ── Supervisor ──
    path("supervisor/override/", SupervisorOverrideView.as_view(), name="supervisor_override"),

    # ── Admin ──
    path("admin/types/", VisaTypeManagementView.as_view(), name="visa_types"),
    path("admin/types/<int:pk>/toggle/", VisaTypeToggleView.as_view(), name="toggle_visa_type"),
    path("admin/reports/", SystemReportsView.as_view(), name="reports"),

    # ── Interview (officer) ──
    path("interview/schedule/<uuid:pk>/", ScheduleInterviewView.as_view(), name="schedule_interview"),
    path("interview/<uuid:pk>/complete/", MarkInterviewCompletedView.as_view(), name="complete_interview"),
    path("interview/<uuid:pk>/cancel/", CancelInterviewView.as_view(), name="cancel_interview"),
    path("interview/application/<uuid:pk>/", ApplicationInterviewsView.as_view(), name="application_interviews"),

    # ── Interview (applicant) ──
    path("my-interviews/<uuid:pk>/", ApplicantInterviewsView.as_view(), name="applicant_interviews"),

    # ── Visa download ──
    path("visa/<uuid:pk>/", VisaDownloadPageView.as_view(), name="visa_download"),
    path("visa/<uuid:pk>/pdf/", VisaDownloadFileView.as_view(), name="visa_download_pdf"),

    # ── Visa issuance (officer) ──
    path("issue/<uuid:pk>/", IssueVisaView.as_view(), name="issue_visa"),
]

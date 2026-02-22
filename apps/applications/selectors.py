from django.shortcuts import get_object_or_404

from apps.applications.choices import ApplicationStatus
from apps.applications.models import VisaApplication


def get_applicant_applications(user):
    return (
        VisaApplication.objects
        .filter(applicant=user, soft_deleted_at__isnull=True)
        .select_related("visa_type")
        .order_by("-created_at")
    )


def get_officer_queue():
    return (
        VisaApplication.objects
        .filter(
            status=ApplicationStatus.UNDER_REVIEW,
            soft_deleted_at__isnull=True,
        )
        .select_related("applicant", "visa_type")
        .order_by("submitted_at")
    )


def get_pending_info_queue():
    return (
        VisaApplication.objects
        .filter(
            status=ApplicationStatus.PENDING_INFO,
            soft_deleted_at__isnull=True,
        )
        .select_related("applicant", "visa_type")
        .order_by("submitted_at")
    )


def get_application_with_documents(application_id):
    return (
        VisaApplication.objects
        .filter(soft_deleted_at__isnull=True)
        .select_related("applicant", "visa_type")
        .prefetch_related("documents", "review_decisions__reviewer", "audit_logs")
        .get(pk=application_id)
    )


def get_application_audit_trail(application_id):
    from apps.audit.models import ApplicationAuditLog

    return (
        ApplicationAuditLog.objects
        .filter(application_id=application_id)
        .select_related("actor")
        .order_by("timestamp")
    )

from __future__ import annotations

from apps.applications.models import VisaApplication
from apps.applications.selectors import (
    get_applicant_applications,
    get_application_audit_trail,
    get_application_with_documents,
)
from apps.applications.services import (
    move_to_under_review,
    run_pre_screening,
    submit_application,
)
from apps.visas.models import InterviewSchedule, VisaDocument


def get_application_interviews(application_id: str):
    """Return all interviews for an application, newest first."""
    return (
        InterviewSchedule.objects
        .filter(application_id=application_id)
        .select_related("officer")
        .order_by("-interview_datetime")
    )


def get_application_visa(application_id: str) -> VisaDocument | None:
    """Return the issued visa document for an application, or None."""
    return (
        VisaDocument.objects
        .filter(application_id=application_id)
        .select_related("created_by")
        .first()
    )

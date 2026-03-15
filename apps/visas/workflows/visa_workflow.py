from __future__ import annotations

from django.db import transaction

from apps.applications.choices import ALLOWED_TRANSITIONS, ApplicationStatus
from apps.applications.models import VisaApplication
from apps.audit.models import ApplicationAuditLog
from apps.reviews.choices import ReviewDecisionChoice
from apps.reviews.models import ReviewDecision
from apps.visas.exceptions import DomainException
from apps.visas.models import VisaDocument
from apps.visas.services.visa_service import create_visa_document


def _transition_status(application, new_status: str) -> None:

    allowed = ALLOWED_TRANSITIONS.get(application.status, set())
    if new_status not in allowed:
        raise DomainException(
            message=(
                f"Transition from {application.status} to {new_status} "
                f"is not allowed."
            ),
            code="invalid_transition",
        )
    application.status = new_status


def approve_application(
    application_id: str,
    officer_id: str,
    reason: str = "",
) -> VisaApplication:

    with transaction.atomic():
        application = (
            VisaApplication.objects
            .select_related("visa_type", "applicant")
            .select_for_update()
            .filter(pk=application_id)
            .first()
        )
        if application is None:
            raise DomainException(
                message=f"Application {application_id} not found.",
                code="application_not_found",
            )

        previous_status = application.status
        _transition_status(application, ApplicationStatus.APPROVED)

        ReviewDecision.objects.create(
            application=application,
            reviewer_id=officer_id,
            decision=ReviewDecisionChoice.APPROVED,
            reason=reason or "Application approved.",
        )

        application.save(update_fields=["status"])

        ApplicationAuditLog(
            application=application,
            previous_status=previous_status,
            new_status=ApplicationStatus.APPROVED,
            actor_id=officer_id,
            reason=reason or "Application approved.",
        ).save()

    return application


def issue_visa(application_id: str, officer_id: str) -> VisaDocument:

    application = (
        VisaApplication.objects
        .select_related("visa_type", "applicant", "payment")
        .filter(pk=application_id)
        .first()
    )
    if application is None:
        raise DomainException(
            message=f"Application {application_id} not found.",
            code="application_not_found",
        )

    from apps.accounts.models import User

    officer = User.objects.filter(pk=officer_id).first()
    if officer is None:
        raise DomainException(
            message=f"Officer {officer_id} not found.",
            code="officer_not_found",
        )

    return create_visa_document(application, officer)

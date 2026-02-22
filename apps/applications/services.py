import datetime

from django.db import transaction
from django.utils import timezone

from apps.applications.choices import ALLOWED_TRANSITIONS, ApplicationStatus
from apps.applications.exceptions import (
    InvalidStateTransition,
    PaymentError,
    RuleViolation,
)
from apps.applications.models import VisaApplication


def _transition_status(
    application: VisaApplication,
    new_status: str,
    actor,
    reason: str = "",
) -> VisaApplication:
    current = application.status
    allowed = ALLOWED_TRANSITIONS.get(current, set())

    if new_status not in allowed:
        raise InvalidStateTransition(
            f"Cannot transition '{application.id}' from {current!r} to {new_status!r}. "
            f"Allowed: {sorted(allowed) if allowed else 'none — terminal state'}."
        )

    update_fields = ["status"]
    application.status = new_status

    if new_status == ApplicationStatus.SUBMITTED:
        application.submitted_at = timezone.now()
        update_fields.append("submitted_at")

    application.save(update_fields=update_fields)

    # Deferred import: importing audit.services at module level would create a
    # circular dependency since audit.models imports nothing from applications.
    from apps.audit.services import log_event

    log_event(
        application=application,
        previous_status=current,
        new_status=new_status,
        actor=actor,
        reason=reason,
    )

    return application


@transaction.atomic
def submit_application(application: VisaApplication, actor) -> VisaApplication:
    return _transition_status(
        application,
        ApplicationStatus.SUBMITTED,
        actor=actor,
        reason="Application submitted by applicant.",
    )


@transaction.atomic
def run_pre_screening(application: VisaApplication) -> VisaApplication:
    # Hard nationality blockers raise BEFORE the status changes so the
    # application stays SUBMITTED and a human can investigate. Soft issues
    # (missing documents) become warnings in the audit reason, not blockers.
    from rules.engine import evaluate
    from apps.documents.services import list_missing_documents

    supplied_types = list(
        application.documents.values_list("document_type", flat=True)
    )

    result = evaluate(
        visa_type_code=application.visa_type.code,
        nationality=application.nationality,
        intended_entry_date=application.intended_entry_date,
        supplied_document_types=supplied_types,
    )

    # Nationality failures are hard stops; document/date failures are surfaced as warnings.
    hard_blockers = [
        code for code in result.failure_codes
        if "NATIONALITY" in code
    ]
    if hard_blockers:
        raise RuleViolation(
            f"Pre-screening hard failure for application {application.id}: "
            + "; ".join(result.explanations),
            failure_codes=result.failure_codes,
        )

    reason = (
        "Pre-screening passed."
        if result.passed
        else "Pre-screening warnings: " + "; ".join(result.explanations)
    )

    return _transition_status(
        application,
        ApplicationStatus.PRE_SCREENING,
        actor=None,  # SYSTEM action
        reason=reason,
    )


@transaction.atomic
def move_to_under_review(application: VisaApplication) -> VisaApplication:
    return _transition_status(
        application,
        ApplicationStatus.UNDER_REVIEW,
        actor=None,  # SYSTEM action
        reason="Pre-screening complete — assigned to officer queue.",
    )


@transaction.atomic
def issue_visa(application: VisaApplication) -> VisaApplication:
    payment = getattr(application, "payment", None)
    if payment is None:
        raise PaymentError(
            f"Application {application.id} has no payment record. "
            "A confirmed payment is required before issuing a visa."
        )

    from apps.payments.choices import PaymentStatus

    if payment.status != PaymentStatus.PAID:
        raise PaymentError(
            f"Application {application.id} payment is {payment.status!r}, "
            "not PAID. Cannot issue visa until payment is confirmed."
        )

    return _transition_status(
        application,
        ApplicationStatus.ISSUED,
        actor=None,  # SYSTEM action
        reason="Payment confirmed — visa issued.",
    )

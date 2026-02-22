from django.db import transaction

from apps.accounts.choices import UserRole
from apps.applications.choices import ApplicationStatus
from apps.applications.exceptions import InvalidStateTransition, PermissionDenied
from apps.applications.models import VisaApplication
from apps.reviews.choices import ReviewDecisionChoice
from apps.reviews.models import ReviewDecision


def _assert_under_review(application: VisaApplication) -> None:
    if application.status != ApplicationStatus.UNDER_REVIEW:
        raise InvalidStateTransition(
            f"Review actions require status UNDER_REVIEW. "
            f"Application {application.id} is currently {application.status!r}."
        )


def _assert_reviewer_role(actor) -> None:
    # SUPERVISOR has override authority but is still gated by this role check.
    if actor.role not in (UserRole.OFFICER, UserRole.SUPERVISOR):
        raise PermissionDenied(
            f"User {actor.id} has role {actor.role!r}. "
            "Only OFFICER or SUPERVISOR may make review decisions."
        )


def _record_decision(
    application: VisaApplication,
    reviewer,
    decision: str,
    reason: str,
) -> ReviewDecision:
    return ReviewDecision.objects.create(
        application=application,
        reviewer=reviewer,
        decision=decision,
        reason=reason,
    )


@transaction.atomic
def approve_application(application: VisaApplication, reviewer) -> ReviewDecision:
    # Approval and issuance are intentionally separate steps: issue_visa() is
    # called only after payment is confirmed, keeping both events auditable.
    _assert_under_review(application)
    _assert_reviewer_role(reviewer)

    from apps.applications.services import _transition_status

    _transition_status(
        application,
        ApplicationStatus.APPROVED,
        actor=reviewer,
        reason=f"Approved by {reviewer.email}.",
    )

    return _record_decision(
        application,
        reviewer,
        ReviewDecisionChoice.APPROVED,
        reason=f"Approved by {reviewer.email}.",
    )


@transaction.atomic
def reject_application(
    application: VisaApplication,
    reviewer,
    reason: str,
) -> ReviewDecision:
    _assert_under_review(application)
    _assert_reviewer_role(reviewer)

    if not reason or not reason.strip():
        from apps.applications.exceptions import RuleViolation
        raise RuleViolation(
            "A written reason is required when rejecting an application.",
            failure_codes=["REJECTION_REASON_MISSING"],
        )

    from apps.applications.services import _transition_status

    _transition_status(
        application,
        ApplicationStatus.REJECTED,
        actor=reviewer,
        reason=reason,
    )

    return _record_decision(
        application,
        reviewer,
        ReviewDecisionChoice.REJECTED,
        reason=reason,
    )


@transaction.atomic
def request_more_info(
    application: VisaApplication,
    reviewer,
    note: str,
) -> ReviewDecision:
    # Moves to PENDING_INFO so the officer queue only shows actionable items.
    _assert_under_review(application)
    _assert_reviewer_role(reviewer)

    from apps.applications.services import _transition_status

    _transition_status(
        application,
        ApplicationStatus.PENDING_INFO,
        actor=reviewer,
        reason=note,
    )

    return _record_decision(
        application,
        reviewer,
        ReviewDecisionChoice.REQUEST_INFO,
        reason=note,
    )

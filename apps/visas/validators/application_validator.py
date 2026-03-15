from __future__ import annotations

from datetime import date

from apps.applications.choices import ApplicationStatus
from apps.payments.choices import PaymentStatus
from apps.visas.exceptions import DomainException


def validate_application_for_submission(application) -> None:
    """
    Ensure *application* contains all required information before it
    may transition from DRAFT → SUBMITTED.

    Raises ``DomainException`` when any mandatory field is missing or
    invalid.
    """
    errors: list[str] = []

    if not application.passport_number:
        errors.append("Passport number is required.")

    if not application.passport_expiry:
        errors.append("Passport expiry date is required.")
    elif application.passport_expiry <= date.today():
        errors.append("Passport must not be expired at the time of submission.")

    if not application.visa_type_id:
        errors.append("A visa type must be selected.")

    if not application.documents.exists():
        errors.append("At least one supporting document must be uploaded.")

    if errors:
        raise DomainException(
            message=" | ".join(errors),
            code="invalid_submission",
        )


def validate_application_for_visa_generation(application) -> None:
    """
    Ensure *application* satisfies every prerequisite for visa
    document generation:

    1. Application is in APPROVED status.
    2. Payment has been confirmed (PAID).
    3. If an interview was required, it has been completed.

    Raises ``DomainException`` on any unmet condition.
    """
    if application.status != ApplicationStatus.APPROVED:
        raise DomainException(
            message=(
                f"Application must be in APPROVED status to issue a visa "
                f"(current: {application.status})."
            ),
            code="not_approved",
        )

    payment = getattr(application, "payment", None)
    if payment is None or payment.status != PaymentStatus.PAID:
        raise DomainException(
            message="Payment must be confirmed before a visa can be issued.",
            code="payment_not_confirmed",
        )

    if application.requires_interview and not application.interview_completed:
        raise DomainException(
            message="The required interview has not been completed.",
            code="interview_incomplete",
        )

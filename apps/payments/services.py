import decimal

from django.db import transaction
from django.utils import timezone

from apps.applications.exceptions import PaymentError
from apps.payments.choices import PaymentStatus
from apps.payments.models import Payment


@transaction.atomic
def mark_as_paid(application, reference: str) -> Payment:
    try:
        payment = Payment.objects.select_for_update().get(application=application)
    except Payment.DoesNotExist:
        raise PaymentError(
            f"No payment record found for application {application.id}. "
            "A payment record must be created before it can be confirmed."
        )

    if payment.status == PaymentStatus.PAID:
        raise PaymentError(
            f"Application {application.id} has already been marked as paid "
            f"(reference: {payment.reference!r}). Double-payment prevented."
        )

    if payment.reference != reference:
        raise PaymentError(
            f"Reference mismatch for application {application.id}. "
            f"Expected {payment.reference!r}, received {reference!r}."
        )

    payment.status = PaymentStatus.PAID
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "paid_at"])

    from apps.audit.services import log_event

    log_event(
        application=application,
        previous_status=application.status,
        new_status=application.status,  # status unchanged; payment event only
        actor=None,
        reason=f"Payment confirmed. Reference: {reference}.",
    )

    return payment


@transaction.atomic
def create_payment_record(application, amount: decimal.Decimal, reference: str) -> Payment:
    if Payment.objects.filter(application=application).exists():
        raise PaymentError(
            f"A payment record already exists for application {application.id}."
        )

    if amount <= 0:
        raise PaymentError(
            f"Payment amount must be positive. Received: {amount}."
        )

    return Payment.objects.create(
        application=application,
        amount=amount,
        reference=reference,
        status=PaymentStatus.PENDING,
    )

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.models import ApplicationAuditLog
from apps.payments.choices import PaymentStatus
from apps.payments.models import Payment
from apps.visas.exceptions import DomainException


def confirm_payment(payment_id: str, actor_id: str | None = None) -> Payment:
    with transaction.atomic():
        payment = (
            Payment.objects
            .select_related("application")
            .select_for_update()
            .filter(pk=payment_id)
            .first()
        )
        if payment is None:
            raise DomainException(
                message=f"Payment {payment_id} not found.",
                code="payment_not_found",
            )
        if payment.status != PaymentStatus.PENDING:
            raise DomainException(
                message=f"Payment is not in PENDING status (current: {payment.status}).",
                code="invalid_payment_status",
            )

        payment.status = PaymentStatus.PAID
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])

        application = payment.application
        ApplicationAuditLog(
            application=application,
            previous_status=application.status,
            new_status=application.status,
            actor_id=actor_id,
            reason=f"Payment confirmed — reference {payment.reference}.",
        ).save()

    return payment

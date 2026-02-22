"""Models for the payments app.

Payment has a OneToOne relationship with VisaApplication — exactly one
payment record per application.  UUID PK because payment IDs appear in
receipts and may be shared with external payment gateways.
"""

import uuid
from django.db import models

from .choices import PaymentStatus


class Payment(models.Model):
    """
    Payment record linked 1-to-1 with a visa application.

    UUID PK — payment IDs are shared externally (receipts, gateway callbacks)
    so sequential integers must not be used.

    Indexing rationale:
      - status: reconciliation and reporting jobs filter by PENDING/PAID.
      - reference: payment gateway callbacks look up records by unique
        reference; fast lookup is critical for webhook response time.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    application = models.OneToOneField(
        "applications.VisaApplication",
        on_delete=models.PROTECT,   # PROTECT: financial record must outlive application
        related_name="payment",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,              # reconciliation queries filter by status
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,              # gateway callbacks hit this field with every notification
        help_text="Unique reference issued by the payment gateway.",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "payments_payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            # Reconciliation: all PENDING payments older than N days.
            models.Index(fields=["status", "paid_at"], name="idx_payment_status_paid"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["reference"], name="uq_payment_reference"),
        ]

    def __str__(self) -> str:
        return f"Payment {self.reference} [{self.status}]"


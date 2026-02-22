"""Models for the applications app.

VisaApplication is the central domain object.  Every other model (documents,
payments, reviews, audit logs) references it.  Design rules enforced here:

  - UUID PK: applications are referenced externally (status URLs, emails).
  - No CASCADE deletes: we never silently destroy related data.
  - Soft-delete only: soft_deleted_at is set instead of calling .delete().
  - Status is indexed for queue and reporting queries.
"""

import uuid
from django.conf import settings
from django.db import models

from .choices import ApplicationStatus


class VisaApplication(models.Model):
    """
    A single visa application submitted by an applicant.

    Indexing rationale:
      - status: officer queue and reporting queries always filter by status.
      - (applicant, created_at): applicant dashboard paginates their own
        applications ordered by creation time — compound index covers both.
      - submitted_at: supervisor SLA dashboards filter/sort by submission date.

    Soft-delete:
      soft_deleted_at being non-null means the record is logically deleted.
      Physical rows are retained for audit and compliance purposes.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # PROTECT: never silently delete an applicant
        related_name="applications",
        db_index=True,
    )
    visa_type = models.ForeignKey(
        "visas.VisaType",
        on_delete=models.PROTECT,   # PROTECT: preserve historical data if type retired
        related_name="applications",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        db_index=True,              # officer queue filters heavily by status
    )
    nationality = models.CharField(
        max_length=2,
        help_text="ISO 3166-1 alpha-2 country code, e.g. 'NG'.",
    )
    purpose_of_travel = models.CharField(max_length=255)
    intended_entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,              # SLA reports filter/sort on submission date
    )
    soft_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Non-null means this record is logically deleted.",
    )

    class Meta:
        db_table = "applications_visaapplication"
        verbose_name = "Visa Application"
        verbose_name_plural = "Visa Applications"
        indexes = [
            # Applicant dashboard: list own applications newest-first.
            models.Index(
                fields=["applicant", "created_at"],
                name="idx_app_applicant_created",
            ),
            # Supervisor/reporting: filter active (non-deleted) records by status.
            models.Index(
                fields=["status", "soft_deleted_at"],
                name="idx_app_status_softdel",
            ),
        ]

    def __str__(self) -> str:
        return f"Application {self.id} [{self.status}]"


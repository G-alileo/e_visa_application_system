import uuid
from django.conf import settings
from django.db import models

from .choices import ApplicationStatus


class VisaApplication(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   
        related_name="applications",
        db_index=True,
    )
    visa_type = models.ForeignKey(
        "visas.VisaType",
        on_delete=models.PROTECT,   
        related_name="applications",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        db_index=True,              
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
        db_index=True,              
    )
    soft_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Non-null means this record is logically deleted.",
    )

    requires_interview = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates whether the application requires an interview before final decision.",
    )
    interview_completed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Tracks whether the scheduled interview has been conducted.",
    )

    passport_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        db_index=True,
        help_text="Applicant's passport number.",
    )
    passport_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Passport expiry date.",
    )
    place_of_issue = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Place where the passport was issued.",
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Applicant's full legal name as on passport.",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Applicant's date of birth.",
    )
    gender = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Applicant's gender.",
    )

    class Meta:
        db_table = "applications_visaapplication"
        verbose_name = "Visa Application"
        verbose_name_plural = "Visa Applications"
        indexes = [
            models.Index(
                fields=["applicant", "created_at"],
                name="idx_app_applicant_created",
            ),
            models.Index(
                fields=["status", "soft_deleted_at"],
                name="idx_app_status_softdel",
            ),
        ]

    def __str__(self) -> str:
        return f"Application {self.id} [{self.status}]"


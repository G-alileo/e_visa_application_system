import uuid

from django.conf import settings
from django.db import models

from .choices import InterviewStatus


class VisaType(models.Model):
    id = models.BigAutoField(primary_key=True)

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,          
        help_text="Short unique code for this visa type, e.g. TOURIST_30.",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Application fee in the system's base currency.",
    )
    max_stay_days = models.PositiveIntegerField(
        help_text="Maximum number of days the holder may stay per visit.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,         
    )

    class Meta:
        db_table = "visas_visatype"
        verbose_name = "Visa Type"
        verbose_name_plural = "Visa Types"
        indexes = [
            models.Index(fields=["is_active", "name"], name="idx_visatype_active_name"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class VisaDocument(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    application = models.OneToOneField(
        "applications.VisaApplication",
        on_delete=models.PROTECT,
        related_name="visa_document",
        help_text="One visa document per approved application.",
    )
    visa_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Globally unique visa identifier, e.g. EVISA-2026-000234.",
    )
    pdf_file = models.FileField(
        upload_to="visas/",
        help_text="Stored visa PDF document.",
    )
    issued_at = models.DateTimeField(
        db_index=True,
        help_text="Timestamp when the visa was officially issued.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_visas",
        help_text="Officer or system actor who triggered issuance.",
    )

    class Meta:
        db_table = "visas_visadocument"
        verbose_name = "Visa Document"
        verbose_name_plural = "Visa Documents"
        indexes = [
            models.Index(
                fields=["issued_at"],
                name="idx_visadoc_issued_at",
            ),
            models.Index(
                fields=["created_at"],
                name="idx_visadoc_created_at",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["visa_number"],
                name="uq_visadoc_visa_number",
            ),
            models.UniqueConstraint(
                fields=["application"],
                name="uq_visadoc_application",
            ),
        ]

    def __str__(self) -> str:
        return f"Visa {self.visa_number} for application {self.application_id}"


class InterviewSchedule(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    application = models.ForeignKey(
        "applications.VisaApplication",
        on_delete=models.PROTECT,
        related_name="interviews",
        db_index=True,
    )
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="scheduled_interviews",
        db_index=True,
    )
    interview_datetime = models.DateTimeField(
        db_index=True,
        help_text="Scheduled date and time for the interview.",
    )
    google_meet_link = models.URLField(
        max_length=255,
        blank=True,
        default="",
        help_text="Google Meet link for the interview session.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes or instructions for the interview.",
    )
    status = models.CharField(
        max_length=10,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "visas_interviewschedule"
        verbose_name = "Interview Schedule"
        verbose_name_plural = "Interview Schedules"
        indexes = [
            models.Index(
                fields=["application", "interview_datetime"],
                name="idx_interview_app_dt",
            ),
            models.Index(
                fields=["officer", "interview_datetime"],
                name="idx_interview_officer_dt",
            ),
            models.Index(
                fields=["status", "interview_datetime"],
                name="idx_interview_status_dt",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Interview {self.id} — {self.status} "
            f"on {self.interview_datetime:%Y-%m-%d %H:%M}"
        )


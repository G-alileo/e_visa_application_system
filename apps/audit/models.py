from django.conf import settings
from django.db import models


class ApplicationAuditLog(models.Model):
    application = models.ForeignKey(
        "applications.VisaApplication",
        on_delete=models.PROTECT,   # PROTECT: audit trail must never be silently removed
        related_name="audit_logs",
        db_index=True,
    )
    previous_status = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Status before the transition; empty string for the initial insert.",
    )
    new_status = models.CharField(max_length=20)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # SET_NULL: log survives even if the user is deleted
        related_name="audit_actions",
        db_index=True,
        help_text="The user who triggered the transition, or NULL for SYSTEM actions.",
    )
    reason = models.TextField(
        blank=True,
        default="",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_applicationauditlog"
        verbose_name = "Application Audit Log"
        verbose_name_plural = "Application Audit Logs"
        indexes = [
            models.Index(
                fields=["application", "timestamp"],
                name="idx_audit_app_timestamp",
            ),
            models.Index(
                fields=["actor", "timestamp"],
                name="idx_audit_actor_timestamp",
            ),
        ]

    def save(self, *args, **kwargs) -> None:
        # Overriding save() to block updates: if pk is set the row already exists.
        # Django's ORM uses save() for both INSERT and UPDATE; checking pk distinguishes them.
        if self.pk is not None:
            raise PermissionError(
                "ApplicationAuditLog records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:  # type: ignore[override]
        raise PermissionError(
            "ApplicationAuditLog records are immutable and cannot be deleted."
        )

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] {self.application_id}: "
            f"{self.previous_status!r} → {self.new_status!r}"
        )


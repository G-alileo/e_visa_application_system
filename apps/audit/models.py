"""Models for the audit app.

ApplicationAuditLog is an IMMUTABLE log of every status transition.
Records must never be updated or deleted after creation — enforced at
the model layer by overriding save() and delete().
"""

from django.conf import settings
from django.db import models


class ApplicationAuditLog(models.Model):
    """
    Immutable record of a single status transition on a visa application.

    BigAutoField PK: high-volume append-only table; internal ID only.

    Immutability contract:
      - save() raises if the record already has a PK (i.e., is an update).
      - delete() is blocked unconditionally.
      Both overrides ensure that even Python-layer code cannot corrupt the log.

    actor is nullable to support SYSTEM-initiated transitions (e.g., an
    automated expiry job) where no human user is involved.

    Indexing rationale:
      - (application, timestamp): the primary audit-trail query is
        "show me all transitions for application X in chronological order".
        The compound index satisfies this with a single B-tree scan.
      - (actor, timestamp): compliance queries ask "what did officer Y do
        and when?" — covered without reading the application column.
    """

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
            # Primary audit-trail read pattern: all events for one application.
            models.Index(
                fields=["application", "timestamp"],
                name="idx_audit_app_timestamp",
            ),
            # Compliance query: all actions by a specific actor over a time window.
            models.Index(
                fields=["actor", "timestamp"],
                name="idx_audit_actor_timestamp",
            ),
        ]

    # ── Immutability enforcement ──────────────────────────────────────────────

    def save(self, *args, **kwargs) -> None:
        """Allow INSERT only. Raise on any attempt to UPDATE an existing row."""
        if self.pk is not None:
            raise PermissionError(
                "ApplicationAuditLog records are immutable and cannot be updated."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:  # type: ignore[override]
        """Block all deletions unconditionally."""
        raise PermissionError(
            "ApplicationAuditLog records are immutable and cannot be deleted."
        )

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] {self.application_id}: "
            f"{self.previous_status!r} → {self.new_status!r}"
        )


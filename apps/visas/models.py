"""Models for the visas app.

VisaType is essentially a configuration / look-up table maintained by
administrators.  Row count stays low (tens, not millions) so a plain
BigAutoField PK is correct here — no need for UUID.
"""

from django.db import models


class VisaType(models.Model):
    """
    Catalogue of visa products offered by the system.

    Indexing rationale:
      - code: unique lookup used when an applicant selects a visa type by
        its short code (e.g., from a URL param or form field).
      - is_active: filtering active types is done on every application-creation
        page; a dedicated index avoids a full table scan even as the table grows.
    """

    # BigAutoField comes from DEFAULT_AUTO_FIELD in settings; declared explicitly
    # here for clarity and migration-stability.
    id = models.BigAutoField(primary_key=True)

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,          # fast lookup by programmatic code (e.g. "TOURIST_30")
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
        db_index=True,          # queries for available visa types always filter on this
    )

    class Meta:
        db_table = "visas_visatype"
        verbose_name = "Visa Type"
        verbose_name_plural = "Visa Types"
        indexes = [
            # Supports admin listing sorted/filtered by active flag + name.
            models.Index(fields=["is_active", "name"], name="idx_visatype_active_name"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


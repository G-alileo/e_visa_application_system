from django.db import models


class VisaType(models.Model):
    # Explicit BigAutoField keeps the PK declaration visible in the model and
    # prevents a future DEFAULT_AUTO_FIELD change from silently altering this table.
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
            models.Index(fields=["is_active", "name"], name="idx_visatype_active_name"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


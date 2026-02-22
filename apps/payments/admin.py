from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin config for Payment.
    Financial records are read-only in the admin; mutations must go through
    the business layer (payments.services) to preserve audit integrity.
    """

    list_display = ("reference", "application", "amount", "status", "paid_at")
    list_filter = ("status",)
    search_fields = ("reference", "application__id", "application__applicant__email")
    ordering = ("-paid_at",)
    readonly_fields = ("id", "reference", "paid_at")  # reference is gateway-issued
    raw_id_fields = ("application",)

    fieldsets = (
        ("Reference",  {"fields": ("id", "reference", "application")}),
        ("Financials", {"fields": ("amount", "status", "paid_at")}),
    )

    def has_add_permission(self, request) -> bool:
        # Payments are created exclusively via the service layer; disallow
        # manual inserts from the admin to prevent bypassing business rules.
        return False

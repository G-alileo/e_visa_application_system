from django.contrib import admin

from .models import VisaApplication


@admin.register(VisaApplication)
class VisaApplicationAdmin(admin.ModelAdmin):
    """
    Admin config for VisaApplication.
    Provides quick status filtering and applicant lookup for support staff.
    """

    list_display = (
        "id",
        "applicant",
        "visa_type",
        "status",
        "nationality",
        "intended_entry_date",
        "submitted_at",
        "created_at",
    )
    list_filter = ("status", "visa_type", "nationality")
    search_fields = ("id", "applicant__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "submitted_at")
    date_hierarchy = "created_at"
    raw_id_fields = ("applicant",)       # UUID PKs render poorly in a dropdown

    fieldsets = (
        ("Identity",     {"fields": ("id", "applicant", "visa_type")}),
        ("Details",      {"fields": ("status", "nationality", "purpose_of_travel", "intended_entry_date")}),
        ("Timestamps",   {"fields": ("created_at", "submitted_at", "soft_deleted_at")}),
    )

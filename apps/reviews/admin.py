from django.contrib import admin

from .models import ReviewDecision


@admin.register(ReviewDecision)
class ReviewDecisionAdmin(admin.ModelAdmin):
    """
    Admin config for ReviewDecision.
    Decisions are immutable once recorded; the admin exposes them in
    read-only mode so supervisors can audit officer activity without
    risking accidental edits.
    """

    list_display = ("id", "application", "reviewer", "decision", "created_at")
    list_filter = ("decision",)
    search_fields = (
        "application__id",
        "application__applicant__email",
        "reviewer__email",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "application", "reviewer", "decision", "reason", "created_at")
    raw_id_fields = ()   # raw_id_fields only applies to editable FKs; all are readonly here

    fieldsets = (
        ("Decision",   {"fields": ("id", "application", "reviewer", "decision")}),
        ("Detail",     {"fields": ("reason",)}),
        ("Timestamps", {"fields": ("created_at",)}),
    )

    def has_add_permission(self, request) -> bool:
        # Decisions are created exclusively via the review service layer.
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        # Review decisions are immutable; block edits entirely.
        return False

from django.contrib import admin

from .models import ApplicationDocument


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    """
    Admin config for ApplicationDocument.
    Primarily used by support staff to verify uploaded documents and
    investigate failed upload issues.
    """

    list_display = (
        "id",
        "application",
        "document_type",
        "verified",
        "uploaded_at",
    )
    list_filter = ("document_type", "verified")
    search_fields = ("application__id", "application__applicant__email")
    ordering = ("-uploaded_at",)
    readonly_fields = ("id", "uploaded_at")
    raw_id_fields = ("application",)

    fieldsets = (
        ("Document",   {"fields": ("id", "application", "document_type", "file_path")}),
        ("Verification",{"fields": ("verified",)}),
        ("Timestamps", {"fields": ("uploaded_at",)}),
    )

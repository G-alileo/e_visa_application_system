from django.contrib import admin

from .models import ApplicationAuditLog


@admin.register(ApplicationAuditLog)
class ApplicationAuditLogAdmin(admin.ModelAdmin):
    """
    Admin config for ApplicationAuditLog.
    Audit logs are append-only by design (the model raises PermissionError
    on save/delete of existing rows).  The admin mirrors that contract:
    all fields are read-only and add/change/delete permissions are removed.
    """

    list_display = (
        "id",
        "application",
        "previous_status",
        "new_status",
        "actor",
        "timestamp",
    )
    list_filter = ("new_status", "previous_status")
    search_fields = ("application__id", "actor__email")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"
    # All fields are readonly — the log is a sealed audit trail.
    readonly_fields = (
        "id",
        "application",
        "previous_status",
        "new_status",
        "actor",
        "reason",
        "timestamp",
    )

    fieldsets = (
        ("Transition",  {"fields": ("id", "application", "previous_status", "new_status")}),
        ("Actor",       {"fields": ("actor", "reason")}),
        ("Timestamps",  {"fields": ("timestamp",)}),
    )

    def has_add_permission(self, request) -> bool:
        # Audit entries are created exclusively by the business layer.
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        # The audit log is immutable; no edits are permitted via the admin.
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        # Deleting audit logs would violate the integrity of the audit trail.
        return False

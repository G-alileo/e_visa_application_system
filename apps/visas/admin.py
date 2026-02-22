from django.contrib import admin

from .models import VisaType


@admin.register(VisaType)
class VisaTypeAdmin(admin.ModelAdmin):
    """
    Admin config for VisaType.
    Allows administrators to manage available visa products from the admin panel
    in addition to the front-end visa management view.
    """

    list_display = ("code", "name", "fee_amount", "max_stay_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)
    list_editable = ("is_active",)   # toggle active state directly in the changelist
    readonly_fields = ("id",)

    fieldsets = (
        ("Identity",    {"fields": ("id", "code", "name", "description")}),
        ("Pricing",     {"fields": ("fee_amount", "max_stay_days")}),
        ("Availability",{"fields": ("is_active",)}),
    )

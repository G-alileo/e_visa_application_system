from django.contrib import admin

from .models import InterviewSchedule, VisaDocument, VisaType


@admin.register(VisaType)
class VisaTypeAdmin(admin.ModelAdmin):

    list_display = ("code", "name", "fee_amount", "max_stay_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)
    list_editable = ("is_active",)   
    readonly_fields = ("id",)

    fieldsets = (
        ("Identity",    {"fields": ("id", "code", "name", "description")}),
        ("Pricing",     {"fields": ("fee_amount", "max_stay_days")}),
        ("Availability",{"fields": ("is_active",)}),
    )


@admin.register(VisaDocument)
class VisaDocumentAdmin(admin.ModelAdmin):
    list_display = ("visa_number", "application", "issued_at", "created_by")
    search_fields = ("visa_number",)
    readonly_fields = ("id", "created_at")
    list_filter = ("issued_at",)


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "officer", "interview_datetime", "status")
    list_filter = ("status", "interview_datetime")
    search_fields = ("application__id",)
    readonly_fields = ("id", "created_at", "updated_at")

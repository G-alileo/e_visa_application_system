from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin config for the custom User model.
    Extends Django's built-in UserAdmin so password hashing, change-password
    links, and permission panels work out of the box.
    """

    # Columns shown in the changelist table
    list_display = ("email", "role", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "last_login")

    # BaseUserAdmin references 'username' by default; override to use email.
    fieldsets = (
        (None,              {"fields": ("id", "email", "password")}),
        ("Role",            {"fields": ("role",)}),
        ("Permissions",     {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps",      {"fields": ("created_at", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_superuser"),
        }),
    )

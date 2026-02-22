"""
Centralised role choices for the accounts app.
Keeping enums in choices.py means model fields, serializers, and
business-logic layers share a single source of truth.
"""

from django.db import models


class UserRole(models.TextChoices):
    APPLICANT = "APPLICANT", "Applicant"
    OFFICER = "OFFICER", "Officer"
    SUPERVISOR = "SUPERVISOR", "Supervisor"
    ADMIN = "ADMIN", "Admin"

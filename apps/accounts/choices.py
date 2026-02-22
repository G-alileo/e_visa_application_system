from django.db import models


class UserRole(models.TextChoices):
    APPLICANT = "APPLICANT", "Applicant"
    OFFICER = "OFFICER", "Officer"
    SUPERVISOR = "SUPERVISOR", "Supervisor"
    ADMIN = "ADMIN", "Admin"

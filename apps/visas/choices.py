from django.db import models


class InterviewStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    COMPLETED = "COMPLETED", "Completed"
    MISSED = "MISSED", "Missed"
    CANCELLED = "CANCELLED", "Cancelled"

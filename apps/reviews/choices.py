from django.db import models


class ReviewDecisionChoice(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    REQUEST_INFO = "REQUEST_INFO", "Request More Information"

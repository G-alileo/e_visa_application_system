from django.db import models


class ApplicationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    PRE_SCREENING = "PRE_SCREENING", "Pre-Screening"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    PENDING_INFO = "PENDING_INFO", "Pending Additional Information"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    ISSUED = "ISSUED", "Issued"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


# Terminal states (REJECTED, ISSUED) are absent as keys — they have no valid exit.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    ApplicationStatus.DRAFT: {ApplicationStatus.SUBMITTED},
    ApplicationStatus.SUBMITTED: {ApplicationStatus.PRE_SCREENING},
    ApplicationStatus.PRE_SCREENING: {ApplicationStatus.UNDER_REVIEW},
    ApplicationStatus.UNDER_REVIEW: {
        ApplicationStatus.APPROVED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.PENDING_INFO,
    },
    ApplicationStatus.PENDING_INFO: {ApplicationStatus.UNDER_REVIEW},
    ApplicationStatus.APPROVED: {ApplicationStatus.ISSUED},
}

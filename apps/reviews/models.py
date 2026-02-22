from django.conf import settings
from django.db import models

from .choices import ReviewDecisionChoice


class ReviewDecision(models.Model):
    application = models.ForeignKey(
        "applications.VisaApplication",
        on_delete=models.PROTECT,   # PROTECT: decisions must survive application changes
        related_name="review_decisions",
        db_index=True,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,   # PROTECT: reviews must survive account deactivation
        related_name="review_decisions",
        db_index=True,
    )
    decision = models.CharField(
        max_length=15,
        choices=ReviewDecisionChoice.choices,
        db_index=True,              # aggregate reports filter/group by decision
    )
    reason = models.TextField(
        help_text="Officer's written justification for the decision.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews_reviewdecision"
        verbose_name = "Review Decision"
        verbose_name_plural = "Review Decisions"
        indexes = [
            models.Index(
                fields=["application", "created_at"],
                name="idx_review_app_created",
            ),
            models.Index(
                fields=["reviewer", "created_at"],
                name="idx_review_reviewer_created",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.decision} on {self.application_id} by {self.reviewer_id}"


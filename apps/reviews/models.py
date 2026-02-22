"""Models for the reviews app.

ReviewDecision records each decision made by an officer or supervisor on a
visa application.  Multiple reviews are possible per application (e.g.,
initial review → request info → final review).
"""

from django.conf import settings
from django.db import models

from .choices import ReviewDecisionChoice


class ReviewDecision(models.Model):
    """
    A single review decision made by an officer/supervisor.

    BigAutoField PK: review records are internal, high-volume, and never
    referenced externally by ID.

    Indexing rationale:
      - decision: reporting queries aggregate outcomes by decision type.
      - reviewer: officer performance dashboards filter by reviewer.
      - (application, created_at): timeline views fetch all decisions for
        one application ordered by time — compound index covers both.
    """

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
            # Application timeline: ordered list of decisions per application.
            models.Index(
                fields=["application", "created_at"],
                name="idx_review_app_created",
            ),
            # Officer workload / performance queries.
            models.Index(
                fields=["reviewer", "created_at"],
                name="idx_review_reviewer_created",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.decision} on {self.application_id} by {self.reviewer_id}"


"""Models for the documents app.

ApplicationDocument stores metadata about files uploaded by applicants.
Actual file bytes live on the filesystem / object-storage; file_path is
the logical reference to that storage location.
"""

from django.db import models

from .choices import DocumentType


class ApplicationDocument(models.Model):
    """
    A single supporting document attached to a visa application.

    BigAutoField PK: documents are internal records, never referenced
    externally by ID, so a sequential integer is appropriate and cheaper
    than UUID for high-volume tables.

    Indexing rationale:
      - application: officers retrieve all documents for a given application;
        this is the dominant access pattern.
      - document_type: officers may need to check whether a specific document
        type has been supplied (e.g., has the passport scan been uploaded?).
      - verified: supervisor dashboards query unverified documents across all
        applications to identify pending verification work.
    """

    application = models.ForeignKey(
        "applications.VisaApplication",
        on_delete=models.PROTECT,   # PROTECT: retain evidence even if application changes
        related_name="documents",
        db_index=True,
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        db_index=True,
    )
    file_path = models.CharField(
        max_length=512,
        help_text="Relative path or object-storage key for the uploaded file.",
    )
    verified = models.BooleanField(
        default=False,
        db_index=True,              # index lets verification dashboard query unverified docs
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "documents_applicationdocument"
        verbose_name = "Application Document"
        verbose_name_plural = "Application Documents"
        indexes = [
            # Covers the common query: "all unverified docs for this application".
            models.Index(
                fields=["application", "verified"],
                name="idx_doc_app_verified",
            ),
            # Officer checklist: has document_type X been uploaded for application Y?
            models.Index(
                fields=["application", "document_type"],
                name="idx_doc_app_type",
            ),
        ]
        constraints = [
            # An application should not have duplicate document types
            # (one passport scan per application, etc.).
            models.UniqueConstraint(
                fields=["application", "document_type"],
                name="uq_doc_application_type",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.document_type} for application {self.application_id}"


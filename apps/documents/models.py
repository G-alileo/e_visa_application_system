from django.db import models

from .choices import DocumentType


class ApplicationDocument(models.Model):
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
            models.Index(
                fields=["application", "verified"],
                name="idx_doc_app_verified",
            ),
            models.Index(
                fields=["application", "document_type"],
                name="idx_doc_app_type",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["application", "document_type"],
                name="uq_doc_application_type",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.document_type} for application {self.application_id}"


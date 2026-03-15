from __future__ import annotations

from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.applications.choices import ApplicationStatus
from apps.audit.models import ApplicationAuditLog
from apps.visas.exceptions import DomainException
from apps.visas.models import VisaDocument
from apps.visas.validators.application_validator import (
    validate_application_for_visa_generation,
)


def _generate_visa_number() -> str:
    year = timezone.now().year
    last_doc = (
        VisaDocument.objects
        .filter(visa_number__startswith=f"EVISA-{year}-")
        .order_by("-visa_number")
        .values_list("visa_number", flat=True)
        .first()
    )
    if last_doc:
        last_seq = int(last_doc.rsplit("-", 1)[-1])
    else:
        last_seq = 0
    return f"EVISA-{year}-{last_seq + 1:06d}"


def generate_visa_pdf(application) -> bytes:
    from weasyprint import HTML

    context = {
        "application": application,
        "applicant": application.applicant,
        "visa_type": application.visa_type,
        "issued_date": timezone.now(),
    }

    html_string = render_to_string("visa_documents/visa_template.html", context)
    pdf_bytes: bytes = HTML(string=html_string).write_pdf()
    return pdf_bytes


def create_visa_document(application, officer) -> VisaDocument:
    validate_application_for_visa_generation(application)

    visa_number = _generate_visa_number()
    pdf_bytes = generate_visa_pdf(application)
    now = timezone.now()

    filename = f"visa_{visa_number}.pdf"

    with transaction.atomic():
        visa_doc = VisaDocument(
            application=application,
            visa_number=visa_number,
            issued_at=now,
            created_by=officer,
        )
        visa_doc.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        visa_doc.save()

        previous_status = application.status
        application.status = ApplicationStatus.ISSUED
        application.save(update_fields=["status"])

        ApplicationAuditLog(
            application=application,
            previous_status=previous_status,
            new_status=ApplicationStatus.ISSUED,
            actor=officer,
            reason=f"Visa issued — {visa_number}.",
        ).save()

    return visa_doc

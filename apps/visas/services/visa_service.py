from __future__ import annotations

import re

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


_VISA_TEMPLATE_CSS_VARIABLES = {
    "--cream": "#F8F0DC",
    "--cream-dark": "#EFE3C2",
    "--gold": "#B07D2A",
    "--gold-light": "#C9950C",
    "--gold-pale": "#F0D898",
    "--brown-deep": "#2C1A0A",
    "--brown-mid": "#4A2F10",
    "--brown-soft": "#7A5C2E",
    "--olive": "#3D3A1E",
    "--green-seal": "#1A6B4A",
    "--red-strip": "#8B1A1A",
    "--text-main": "#1E1409",
    "--text-muted": "#6B5333",
}

_CSS_VAR_PATTERN = re.compile(
    r"var\(\s*(--[a-zA-Z0-9_-]+)\s*(?:,\s*([^\)]+?)\s*)?\)"
)


def _resolve_css_variables(css_or_html: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        fallback = match.group(2)
        if var_name in _VISA_TEMPLATE_CSS_VARIABLES:
            return _VISA_TEMPLATE_CSS_VARIABLES[var_name]
        if fallback is not None:
            return fallback.strip()
        return match.group(0)

    return _CSS_VAR_PATTERN.sub(_replace, css_or_html)


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


def generate_visa_pdf(application, visa_number: str) -> bytes:
    import io
    from xhtml2pdf import pisa

    context = {
        "application": application,
        "applicant": application.applicant,
        "visa_type": application.visa_type,
        "issued_date": timezone.now(),
        "visa_number": visa_number,
    }

    html_string = render_to_string("visa_documents/visa_template.html", context)
    html_string = _resolve_css_variables(html_string)
    buffer = io.BytesIO()
    result = pisa.CreatePDF(html_string, dest=buffer)
    if result.err:
        raise DomainException("Failed to generate visa PDF.")
    return buffer.getvalue()


def create_visa_document(application, officer) -> VisaDocument:
    validate_application_for_visa_generation(application)

    visa_number = _generate_visa_number()
    pdf_bytes = generate_visa_pdf(application, visa_number=visa_number)
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

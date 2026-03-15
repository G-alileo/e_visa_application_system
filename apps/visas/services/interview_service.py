from __future__ import annotations

from datetime import datetime as dt

from django.db import transaction
from django.utils import timezone

from apps.applications.models import VisaApplication
from apps.audit.models import ApplicationAuditLog
from apps.visas.choices import InterviewStatus
from apps.visas.exceptions import DomainException
from apps.visas.models import InterviewSchedule


def schedule_interview(
    application_id: str,
    officer_id: str,
    interview_datetime: dt,
    meet_link: str = "",
    notes: str = "",
) -> InterviewSchedule:
    """
    Create a new ``InterviewSchedule`` for the given application and
    mark the application as requiring an interview.
    """
    with transaction.atomic():
        application = (
            VisaApplication.objects
            .select_for_update()
            .filter(pk=application_id)
            .first()
        )
        if application is None:
            raise DomainException(
                message=f"Application {application_id} not found.",
                code="application_not_found",
            )

        interview = InterviewSchedule.objects.create(
            application=application,
            officer_id=officer_id,
            interview_datetime=interview_datetime,
            google_meet_link=meet_link,
            notes=notes,
            status=InterviewStatus.SCHEDULED,
        )

        application.requires_interview = True
        application.save(update_fields=["requires_interview"])

        ApplicationAuditLog(
            application=application,
            previous_status=application.status,
            new_status=application.status,
            actor_id=officer_id,
            reason=f"Interview scheduled for {interview_datetime:%Y-%m-%d %H:%M}.",
        ).save()

    return interview


def mark_interview_completed(interview_id: str, actor_id: str | None = None) -> InterviewSchedule:
    """
    Mark an interview as COMPLETED and flag the parent application
    accordingly.
    """
    interview = (
        InterviewSchedule.objects
        .select_related("application")
        .filter(pk=interview_id)
        .first()
    )
    if interview is None:
        raise DomainException(
            message=f"Interview {interview_id} not found.",
            code="interview_not_found",
        )
    if interview.status != InterviewStatus.SCHEDULED:
        raise DomainException(
            message=f"Only SCHEDULED interviews can be completed (current: {interview.status}).",
            code="invalid_interview_status",
        )

    with transaction.atomic():
        interview.status = InterviewStatus.COMPLETED
        interview.save(update_fields=["status", "updated_at"])

        application = interview.application
        application.interview_completed = True
        application.save(update_fields=["interview_completed"])

        ApplicationAuditLog(
            application=application,
            previous_status=application.status,
            new_status=application.status,
            actor_id=actor_id or interview.officer_id,
            reason="Interview completed.",
        ).save()

    return interview


def cancel_interview(interview_id: str, actor_id: str | None = None) -> InterviewSchedule:
    """
    Cancel a SCHEDULED interview.  Does **not** alter the parent
    application's ``requires_interview`` flag — an officer may schedule
    a replacement.
    """
    interview = (
        InterviewSchedule.objects
        .select_related("application")
        .filter(pk=interview_id)
        .first()
    )
    if interview is None:
        raise DomainException(
            message=f"Interview {interview_id} not found.",
            code="interview_not_found",
        )
    if interview.status != InterviewStatus.SCHEDULED:
        raise DomainException(
            message=f"Only SCHEDULED interviews can be cancelled (current: {interview.status}).",
            code="invalid_interview_status",
        )

    with transaction.atomic():
        interview.status = InterviewStatus.CANCELLED
        interview.save(update_fields=["status", "updated_at"])

        ApplicationAuditLog(
            application=interview.application,
            previous_status=interview.application.status,
            new_status=interview.application.status,
            actor_id=actor_id or interview.officer_id,
            reason="Interview cancelled.",
        ).save()

    return interview

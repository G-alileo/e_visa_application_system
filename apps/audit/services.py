from apps.audit.models import ApplicationAuditLog


def log_event(
    application,
    previous_status: str,
    new_status: str,
    actor,  # None for SYSTEM-initiated transitions
    reason: str = "",
) -> ApplicationAuditLog:
    return ApplicationAuditLog.objects.create(
        application=application,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        reason=reason,
    )

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.audit.models import ApplicationAuditLog


class AuditLogView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.SUPERVISOR, UserRole.ADMIN]
    template_name = "supervisor/audit_log.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()
        logs = (
            ApplicationAuditLog.objects
            .select_related("application__visa_type", "actor")
            .order_by("-timestamp")
        )
        if query:
            logs = logs.filter(application_id__icontains=query)
        return render(request, self.template_name, {
            "logs": logs[:500],
            "query": query,
        })

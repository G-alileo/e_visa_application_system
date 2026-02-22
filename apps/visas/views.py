import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.applications.choices import ApplicationStatus
from apps.applications.models import VisaApplication
from apps.visas.forms import VisaTypeForm
from apps.visas.models import VisaType


class SupervisorOverrideView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.SUPERVISOR]
    template_name = "supervisor/override.html"

    def get(self, request):
        escalated = (
            VisaApplication.objects
            .filter(status=ApplicationStatus.UNDER_REVIEW, soft_deleted_at__isnull=True)
            .select_related("applicant", "visa_type")
            .order_by("submitted_at")
        )
        recent_rejected = (
            VisaApplication.objects
            .filter(status=ApplicationStatus.REJECTED, soft_deleted_at__isnull=True)
            .select_related("applicant", "visa_type")
            .order_by("-submitted_at")[:20]
        )
        return render(request, self.template_name, {
            "escalated": escalated,
            "recent_rejected": recent_rejected,
            "can_take_action": True,
        })


class VisaTypeManagementView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.ADMIN]
    template_name = "admin/visa_types.html"

    def get(self, request):
        return render(request, self.template_name, {
            "visa_types": VisaType.objects.order_by("name"),
            "form": VisaTypeForm(),
        })

    def post(self, request):
        form = VisaTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Visa type created.")
            return redirect("visas:visa_types")
        return render(request, self.template_name, {
            "visa_types": VisaType.objects.order_by("name"),
            "form": form,
        })


class VisaTypeToggleView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.ADMIN]

    def post(self, request, pk):
        vt = get_object_or_404(VisaType, pk=pk)
        vt.is_active = not vt.is_active
        vt.save(update_fields=["is_active"])
        label = "activated" if vt.is_active else "deactivated"
        messages.success(request, f"'{vt.name}' {label}.")
        return redirect("visas:visa_types")


class SystemReportsView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.ADMIN, UserRole.SUPERVISOR]
    template_name = "admin/reports.html"

    def get(self, request):
        status_counts = dict(
            VisaApplication.objects
            .filter(soft_deleted_at__isnull=True)
            .values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )
        total = sum(status_counts.values())
        issued = status_counts.get(ApplicationStatus.ISSUED, 0)
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        this_month = VisaApplication.objects.filter(
            submitted_at__gte=thirty_days_ago, soft_deleted_at__isnull=True
        ).count()
        approval_rate = round(issued / total * 100, 1) if total > 0 else 0.0
        return render(request, self.template_name, {
            "status_counts": status_counts,
            "status_labels": dict(ApplicationStatus.choices),
            "total": total,
            "issued": issued,
            "this_month": this_month,
            "approval_rate": approval_rate,
            "visa_types": VisaType.objects.order_by("name"),
        })

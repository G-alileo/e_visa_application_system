import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.applications.choices import ApplicationStatus
from apps.applications.models import VisaApplication
from apps.visas.exceptions import DomainException
from apps.visas.forms import InterviewScheduleForm, VisaTypeForm
from apps.visas.models import InterviewSchedule, VisaDocument, VisaType
from apps.visas.services.application_service import (
    get_application_interviews,
    get_application_visa,
)
from apps.visas.services.interview_service import (
    cancel_interview,
    mark_interview_completed,
    schedule_interview,
)
from apps.visas.workflows.visa_workflow import issue_visa


REVIEWER_ROLES = [UserRole.OFFICER, UserRole.SUPERVISOR]


# ── Officer: Schedule Interview ────────────────────────────────────


class ScheduleInterviewView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/schedule_interview.html"

    def get(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, soft_deleted_at__isnull=True,
        )
        return render(request, self.template_name, {
            "application": application,
            "form": InterviewScheduleForm(),
        })

    def post(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, soft_deleted_at__isnull=True,
        )
        form = InterviewScheduleForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "application": application,
                "form": form,
            })
        try:
            schedule_interview(
                application_id=str(application.pk),
                officer_id=str(request.user.pk),
                interview_datetime=form.cleaned_data["interview_datetime"],
                meet_link=form.cleaned_data.get("google_meet_link", ""),
                notes=form.cleaned_data.get("notes", ""),
            )
        except DomainException as exc:
            messages.error(request, exc.message)
            return render(request, self.template_name, {
                "application": application,
                "form": form,
            })
        messages.success(request, "Interview scheduled successfully.")
        return redirect("reviews:review", pk=pk)




class MarkInterviewCompletedView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES

    def post(self, request, pk):
        try:
            interview = mark_interview_completed(
                interview_id=str(pk),
                actor_id=str(request.user.pk),
            )
        except DomainException as exc:
            messages.error(request, exc.message)
            return redirect("reviews:queue")
        messages.success(request, "Interview marked as completed.")
        return redirect("reviews:review", pk=interview.application_id)




class CancelInterviewView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES

    def post(self, request, pk):
        try:
            interview = cancel_interview(
                interview_id=str(pk),
                actor_id=str(request.user.pk),
            )
        except DomainException as exc:
            messages.error(request, exc.message)
            return redirect("reviews:queue")
        messages.success(request, "Interview cancelled.")
        return redirect("reviews:review", pk=interview.application_id)




class IssueVisaView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES

    def post(self, request, pk):
        try:
            visa_doc = issue_visa(
                application_id=str(pk),
                officer_id=str(request.user.pk),
            )
        except DomainException as exc:
            messages.error(request, exc.message)
            return redirect("reviews:review", pk=pk)
        messages.success(request, f"Visa {visa_doc.visa_number} issued successfully.")
        return redirect("reviews:review", pk=pk)




class ApplicationInterviewsView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/interviews.html"

    def get(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, soft_deleted_at__isnull=True,
        )
        interviews = get_application_interviews(str(pk))
        return render(request, self.template_name, {
            "application": application,
            "interviews": interviews,
        })




class ApplicantInterviewsView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/interviews.html"

    def get(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, applicant=request.user,
            soft_deleted_at__isnull=True,
        )
        interviews = get_application_interviews(str(pk))
        return render(request, self.template_name, {
            "application": application,
            "interviews": interviews,
        })




class VisaDownloadPageView(LoginRequiredMixin, View):
    template_name = "applicant/visa_download.html"

    def get(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, soft_deleted_at__isnull=True,
        )
        is_owner = application.applicant_id == request.user.pk
        is_reviewer = request.user.role in (
            UserRole.OFFICER, UserRole.SUPERVISOR, UserRole.ADMIN,
        )
        if not is_owner and not is_reviewer:
            return render(request, "auth/access_denied.html", status=403)

        visa_doc = get_application_visa(str(pk))
        if visa_doc is None:
            raise Http404("No visa has been issued for this application.")

        return render(request, self.template_name, {
            "application": application,
            "visa_document": visa_doc,
            "visa_number": visa_doc.visa_number,
            "visa_type": application.visa_type,
            "issued_date": visa_doc.issued_at,
            "is_owner": is_owner,
        })


class VisaDownloadFileView(LoginRequiredMixin, View):
    """Serve the actual PDF file for download."""

    def get(self, request, pk):
        application = get_object_or_404(
            VisaApplication, pk=pk, soft_deleted_at__isnull=True,
        )
        is_owner = application.applicant_id == request.user.pk
        is_reviewer = request.user.role in (
            UserRole.OFFICER, UserRole.SUPERVISOR, UserRole.ADMIN,
        )
        if not is_owner and not is_reviewer:
            return render(request, "auth/access_denied.html", status=403)

        visa_doc = get_application_visa(str(pk))
        if visa_doc is None or not visa_doc.pdf_file:
            raise Http404("Visa PDF not found.")

        return FileResponse(
            visa_doc.pdf_file.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{visa_doc.visa_number}.pdf",
        )




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

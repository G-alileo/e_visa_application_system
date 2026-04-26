from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.applications.choices import ApplicationStatus
from apps.applications.exceptions import InvalidStateTransition, PermissionDenied, RuleViolation
from apps.applications.models import VisaApplication
from apps.applications.selectors import (
    get_application_audit_trail,
    get_application_with_documents,
    get_officer_queue,
    get_pending_info_queue,
)
from apps.reviews.forms import DecisionReasonForm, RequestInfoForm
from apps.reviews.models import ReviewDecision
from apps.reviews.services import approve_application, reject_application, request_more_info
from apps.visas.models import VisaType


REVIEWER_ROLES = [UserRole.OFFICER, UserRole.SUPERVISOR]


class OfficerQueueView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/queue.html"

    def get(self, request):
        selected_visa_type_id = (request.GET.get("visa_type") or "").strip()
        visa_type_filter_id = int(selected_visa_type_id) if selected_visa_type_id.isdigit() else None

        visa_type_filters = VisaType.objects.filter(is_active=True).order_by("name")
        if (
            visa_type_filter_id is not None
            and not visa_type_filters.filter(pk=visa_type_filter_id).exists()
        ):
            visa_type_filter_id = None
            selected_visa_type_id = ""

        if visa_type_filter_id is None:
            selected_visa_type_id = ""

        queue = get_officer_queue(visa_type_id=visa_type_filter_id)
        pending_info = get_pending_info_queue(visa_type_id=visa_type_filter_id)
        return render(request, self.template_name, {
            "queue": queue,
            "pending_info_queue": pending_info,
            "visa_type_filters": visa_type_filters,
            "selected_visa_type_id": selected_visa_type_id,
            "is_supervisor": request.user.role == UserRole.SUPERVISOR,
        })


class ApplicationReviewView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/review.html"

    def get(self, request, pk):
        try:
            app = get_application_with_documents(pk)
        except VisaApplication.DoesNotExist:
            raise Http404
        audit_trail = get_application_audit_trail(pk)
        can_decide = app.status == ApplicationStatus.UNDER_REVIEW
        return render(request, self.template_name, {
            "application": app,
            "audit_trail": audit_trail,
            "approve_form": DecisionReasonForm(prefix="approve"),
            "reject_form": DecisionReasonForm(prefix="reject"),
            "request_info_form": RequestInfoForm(prefix="info"),
            "can_decide": can_decide,
            "is_supervisor": request.user.role == UserRole.SUPERVISOR,
        })


class ApproveApplicationView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES

    def post(self, request, pk):
        app = get_object_or_404(VisaApplication, pk=pk, soft_deleted_at__isnull=True)
        try:
            approve_application(app, reviewer=request.user)
        except (PermissionDenied, InvalidStateTransition) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Application approved.")
        return redirect("reviews:review", pk=pk)


class RejectApplicationView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES

    def post(self, request, pk):
        app = get_object_or_404(VisaApplication, pk=pk, soft_deleted_at__isnull=True)
        form = DecisionReasonForm(request.POST, prefix="reject")
        if not form.is_valid():
            messages.error(request, "A written reason is required to reject an application.")
            return redirect("reviews:review", pk=pk)
        try:
            reject_application(app, reviewer=request.user, reason=form.cleaned_data["reason"])
        except (PermissionDenied, InvalidStateTransition, RuleViolation) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Application rejected.")
        return redirect("reviews:review", pk=pk)


class RequestMoreInfoView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/request_info.html"

    def get(self, request, pk):
        app = get_object_or_404(VisaApplication, pk=pk, soft_deleted_at__isnull=True)
        return render(request, self.template_name, {
            "application": app,
            "form": RequestInfoForm(),
            "can_request": app.status == ApplicationStatus.UNDER_REVIEW,
        })

    def post(self, request, pk):
        app = get_object_or_404(VisaApplication, pk=pk, soft_deleted_at__isnull=True)
        form = RequestInfoForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "application": app, "form": form,
                "can_request": app.status == ApplicationStatus.UNDER_REVIEW,
            })
        try:
            request_more_info(app, reviewer=request.user, note=form.cleaned_data["note"])
        except (PermissionDenied, InvalidStateTransition) as exc:
            messages.error(request, str(exc))
            return redirect("reviews:review", pk=pk)
        messages.success(request, "Information request sent to applicant.")
        return redirect("reviews:queue")


class DecisionHistoryView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = REVIEWER_ROLES
    template_name = "officer/history.html"

    def get(self, request):
        if request.user.role == UserRole.SUPERVISOR:
            decisions = (
                ReviewDecision.objects
                .select_related("application__visa_type", "reviewer")
                .order_by("-created_at")[:200]
            )
        else:
            decisions = (
                ReviewDecision.objects
                .filter(reviewer=request.user)
                .select_related("application__visa_type")
                .order_by("-created_at")[:200]
            )
        return render(request, self.template_name, {
            "decisions": decisions,
            "is_supervisor": request.user.role == UserRole.SUPERVISOR,
        })

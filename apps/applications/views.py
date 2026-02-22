import uuid as _uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import FormView, View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.applications.choices import ApplicationStatus
from apps.applications.exceptions import InvalidStateTransition, RuleViolation
from apps.applications.forms import CreateApplicationForm
from apps.applications.models import VisaApplication
from apps.applications.selectors import (
    get_applicant_applications,
    get_application_audit_trail,
    get_application_with_documents,
)
from apps.applications.services import move_to_under_review, run_pre_screening, submit_application
from apps.documents.forms import DocumentUploadForm
from apps.documents.models import ApplicationDocument
from apps.documents.services import get_document_summary
from apps.recommendations.services import get_recommendations


class ApplicantDashboardView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/dashboard.html"

    def get(self, request):
        applications = get_applicant_applications(request.user)
        status_labels = dict(ApplicationStatus.choices)
        return render(request, self.template_name, {
            "applications": applications,
            "status_labels": status_labels,
            "can_create": True,
        })


class CreateApplicationView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/create_application.html"
    form_class = CreateApplicationForm

    def form_valid(self, form):
        app = form.save(commit=False)
        app.applicant = self.request.user
        app.status = ApplicationStatus.DRAFT
        app.save()
        return redirect("applications:upload", pk=app.pk)


class UploadDocumentsView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/upload_documents.html"

    def _get_owned(self, request, pk):
        app = get_object_or_404(VisaApplication, pk=pk, soft_deleted_at__isnull=True)
        if app.applicant_id != request.user.pk:
            return None
        return app

    def get(self, request, pk):
        app = self._get_owned(request, pk)
        if app is None:
            return render(request, "auth/access_denied.html", status=403)
        doc_summary = get_document_summary(app)
        can_upload = app.status in (ApplicationStatus.DRAFT, ApplicationStatus.PENDING_INFO)
        return render(request, self.template_name, {
            "application": app,
            "form": DocumentUploadForm(),
            "doc_summary": doc_summary,
            "can_upload": can_upload,
            "can_submit": app.status == ApplicationStatus.DRAFT,
        })

    def post(self, request, pk):
        app = self._get_owned(request, pk)
        if app is None:
            return render(request, "auth/access_denied.html", status=403)
        if app.status not in (ApplicationStatus.DRAFT, ApplicationStatus.PENDING_INFO):
            messages.error(request, "Documents cannot be changed at this stage.")
            return redirect("applications:upload", pk=pk)
        form = DocumentUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {
                "application": app,
                "form": form,
                "doc_summary": get_document_summary(app),
                "can_upload": True,
                "can_submit": app.status == ApplicationStatus.DRAFT,
            })
        from django.conf import settings as _s
        from pathlib import Path
        uploaded = request.FILES["file"]
        upload_dir = Path(_s.MEDIA_ROOT) / "documents" / str(app.pk)
        upload_dir.mkdir(parents=True, exist_ok=True)
        rel_path = f"documents/{app.pk}/{uploaded.name}"
        with open(Path(_s.MEDIA_ROOT) / rel_path, "wb+") as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)
        doc_type = form.cleaned_data["document_type"]
        ApplicationDocument.objects.update_or_create(
            application=app,
            document_type=doc_type,
            defaults={"file_path": rel_path, "verified": False},
        )
        messages.success(request, f"Document '{doc_type}' uploaded.")
        return redirect("applications:upload", pk=pk)


class SubmitApplicationView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]

    def post(self, request, pk):
        app = get_object_or_404(
            VisaApplication, pk=pk, applicant=request.user, soft_deleted_at__isnull=True
        )
        try:
            submit_application(app, actor=request.user)
            from apps.payments.services import create_payment_record
            reference = f"EVS-{str(app.pk)[:8].upper()}-{_uuid.uuid4().hex[:6].upper()}"
            create_payment_record(app, amount=app.visa_type.fee_amount, reference=reference)
            run_pre_screening(app)
            move_to_under_review(app)
        except RuleViolation as exc:
            messages.error(request, f"Submission blocked: {exc}")
            return redirect("applications:upload", pk=pk)
        except InvalidStateTransition as exc:
            messages.error(request, str(exc))
            return redirect("applications:status", pk=pk)
        messages.success(request, "Application submitted and is now under review.")
        return redirect("applications:status", pk=pk)


class ApplicationStatusView(LoginRequiredMixin, View):
    template_name = "applicant/status.html"

    def get(self, request, pk):
        try:
            app = get_application_with_documents(pk)
        except VisaApplication.DoesNotExist:
            raise Http404
        is_owner = app.applicant_id == request.user.pk
        is_reviewer = request.user.role in (UserRole.OFFICER, UserRole.SUPERVISOR, UserRole.ADMIN)
        if not is_owner and not is_reviewer:
            return render(request, "auth/access_denied.html", status=403)
        audit_trail = get_application_audit_trail(pk)
        payment = getattr(app, "payment", None)
        return render(request, self.template_name, {
            "application": app,
            "audit_trail": audit_trail,
            "payment": payment,
            "can_submit": is_owner and app.status == ApplicationStatus.DRAFT,
            "can_upload": is_owner and app.status in (ApplicationStatus.DRAFT, ApplicationStatus.PENDING_INFO),
            "can_pay": is_owner and app.status == ApplicationStatus.APPROVED,
            "can_re_apply": is_owner and app.status == ApplicationStatus.REJECTED,
            "is_owner": is_owner,
            "is_reviewer": is_reviewer,
        })


class RecommendationsView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/recommendations.html"

    def get(self, request, pk):
        app = get_object_or_404(
            VisaApplication, pk=pk, applicant=request.user, soft_deleted_at__isnull=True
        )
        recommendations = get_recommendations(app)
        return render(request, self.template_name, {
            "application": app,
            "recommendations": recommendations,
            "has_recommendations": bool(recommendations),
        })


class ReApplicationView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/re_application.html"
    form_class = CreateApplicationForm

    def dispatch(self, request, *args, **kwargs):
        self.previous_pk = kwargs.get("pk")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["previous_application"] = get_object_or_404(
            VisaApplication, pk=self.previous_pk, applicant=self.request.user
        )
        return ctx

    def get_initial(self):
        prev = get_object_or_404(
            VisaApplication, pk=self.previous_pk, applicant=self.request.user
        )
        return {
            "visa_type": prev.visa_type,
            "nationality": prev.nationality,
            "purpose_of_travel": prev.purpose_of_travel,
        }

    def form_valid(self, form):
        get_object_or_404(
            VisaApplication, pk=self.previous_pk, applicant=self.request.user,
            status=ApplicationStatus.REJECTED,
        )
        new_app = form.save(commit=False)
        new_app.applicant = self.request.user
        new_app.status = ApplicationStatus.DRAFT
        new_app.save()
        messages.success(self.request, "New application created. Please upload your documents.")
        return redirect("applications:upload", pk=new_app.pk)

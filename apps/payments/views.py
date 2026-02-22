from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from apps.accounts.choices import UserRole
from apps.accounts.mixins import RoleRequiredMixin
from apps.applications.choices import ApplicationStatus
from apps.applications.exceptions import InvalidStateTransition, PaymentError
from apps.applications.models import VisaApplication
from apps.applications.services import issue_visa
from apps.payments.services import mark_as_paid


class PaymentView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = [UserRole.APPLICANT]
    template_name = "applicant/payment.html"

    def _get_app(self, request, pk):
        return get_object_or_404(
            VisaApplication, pk=pk, applicant=request.user, soft_deleted_at__isnull=True
        )

    def get(self, request, pk):
        app = self._get_app(request, pk)
        can_pay = app.status == ApplicationStatus.APPROVED
        payment = getattr(app, "payment", None)
        already_paid = payment is not None and payment.status == "PAID"
        return render(request, self.template_name, {
            "application": app,
            "payment": payment,
            "can_pay": can_pay and not already_paid,
            "already_paid": already_paid,
        })

    def post(self, request, pk):
        app = self._get_app(request, pk)
        payment = getattr(app, "payment", None)
        if payment is None:
            messages.error(request, "No payment record found for this application.")
            return redirect("payments:payment", pk=pk)
        try:
            mark_as_paid(app, reference=payment.reference)
            issue_visa(app)
        except (PaymentError, InvalidStateTransition) as exc:
            messages.error(request, str(exc))
            return redirect("payments:payment", pk=pk)
        messages.success(request, "Payment confirmed. Your visa has been issued!")
        return redirect("applications:status", pk=pk)

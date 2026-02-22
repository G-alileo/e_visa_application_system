from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, View

from apps.accounts.choices import UserRole
from apps.accounts.forms import LoginForm, RegisterForm


def _role_home(user) -> str:
    role_map = {
        UserRole.APPLICANT: "applications:dashboard",
        UserRole.OFFICER: "reviews:queue",
        UserRole.SUPERVISOR: "visas:supervisor_override",
        UserRole.ADMIN: "visas:visa_types",
    }
    return reverse(role_map.get(user.role, "applications:dashboard"))


class UserLoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(_role_home(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = authenticate(
            self.request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is None:
            form.add_error(None, "Invalid email or password.")
            return self.form_invalid(form)
        login(self.request, user)
        return redirect(self.request.GET.get("next") or _role_home(user))


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(_role_home(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect(reverse("accounts:login") + "?registered=1")


class UserLogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect("accounts:login")

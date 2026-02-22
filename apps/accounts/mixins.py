from django.shortcuts import render


class RoleRequiredMixin:
    """
    Assumes LoginRequiredMixin is also in the MRO (placed before this in the class definition).
    Renders 403 if the authenticated user's role is not in allowed_roles.
    """
    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role not in self.allowed_roles:
            return render(request, "auth/access_denied.html", {"user": request.user}, status=403)
        return super().dispatch(request, *args, **kwargs)

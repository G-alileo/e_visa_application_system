from apps.accounts.choices import UserRole


def user_role_flags(request):
    if not request.user.is_authenticated:
        return {
            "is_applicant": False,
            "is_officer": False,
            "is_supervisor": False,
            "is_admin": False,
        }
    role = request.user.role
    return {
        "is_applicant": role == UserRole.APPLICANT,
        "is_officer": role == UserRole.OFFICER,
        "is_supervisor": role == UserRole.SUPERVISOR,
        "is_admin": role == UserRole.ADMIN,
    }

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from .choices import UserRole


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        unique=True,
        db_index=True,          # explicit — unique implies index, but clarity is preferred
        max_length=254,
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.APPLICANT,
        db_index=True,          # dashboard and permission queries filter heavily by role
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # required by Django admin
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []        # email is already USERNAME_FIELD

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role", "created_at"], name="idx_user_role_created"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["email"], name="uq_user_email"),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"


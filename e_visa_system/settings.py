import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured


pymysql.version_info = (2, 2, 7, "final", 0)
pymysql.__version__ = "2.2.7"
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _env(key: str, default=None, required: bool = False) -> str:
    """
    Fetch an environment variable.
    Raises ImproperlyConfigured when *required* is True and the key is absent
    so that misconfigured deployments fail immediately on startup.
    """
    value = os.environ.get(key, default)
    if required and (value is None or value == ""):
        raise ImproperlyConfigured(
            f"Required environment variable '{key}' is not set. "
            "Check your .env file or deployment environment."
        )
    return value


SECRET_KEY = _env("SECRET_KEY", required=True)
DEBUG = _env("DEBUG", default="False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    h.strip()
    for h in _env("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts.apps.AccountsConfig",
    "apps.visas.apps.VisasConfig",
    "apps.applications.apps.ApplicationsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.audit.apps.AuditConfig",
    "apps.recommendations.apps.RecommendationsConfig",
    "rest_framework",
    "drf_spectacular",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "e_visa_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.accounts.context_processors.user_role_flags",
            ],
        },
    },
]

WSGI_APPLICATION = "e_visa_system.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": _env("DB_NAME", required=True),
        "USER": _env("DB_USER", required=True),
        "PASSWORD": _env("DB_PASSWORD", default=""),
        "HOST": _env("DB_HOST", default="127.0.0.1"),
        "PORT": _env("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",           # full Unicode including emoji / CJK supplements
            "sql_mode": "STRICT_TRANS_TABLES",  # reject bad data rather than silently coerce
        },
    }
}

AUTH_USER_MODEL = "accounts.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "public",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/applications/dashboard/"
LOGOUT_REDIRECT_URL = "/auth/login/"


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "E-Visa System API",
    "DESCRIPTION": (
        "Internal API powering the E-Visa Application Portal.\n\n"
        "All endpoints require authentication unless stated otherwise.  "
        "Role-based access is enforced at the view level via RoleRequiredMixin."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # hide the schema endpoint from its own output
    "CONTACT": {"name": "E-Visa Support"},
    "LICENSE": {"name": "Proprietary"},
}

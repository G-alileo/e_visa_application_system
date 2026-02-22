"""
Django settings for e_visa_system project.

Environment variables are loaded from .env via python-dotenv.
Required variables raise ImproperlyConfigured on startup so misconfigured
deployments fail loudly rather than silently using wrong values.
"""

import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# ─── PyMySQL as MySQLdb replacement ──────────────────────────────────────────
# pymysql is a pure-Python MySQL client.  Patching it in as MySQLdb lets
# Django's mysql backend work without the native mysqlclient C extension.
# The version_info/version spoof satisfies Django's mysqlclient >= 2.2.1 check.
pymysql.version_info = (2, 2, 7, "final", 0)
pymysql.__version__ = "2.2.7"
pymysql.install_as_MySQLdb()

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root (one level above this settings file).
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


# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = _env("SECRET_KEY", required=True)
DEBUG = _env("DEBUG", default="False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [
    h.strip()
    for h in _env("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")
    if h.strip()
]

# ─── Application definition ──────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps — registered via their AppConfig so the dotted label
    # apps.<name> is used consistently throughout Django internals.
    "apps.accounts.apps.AccountsConfig",
    "apps.visas.apps.VisasConfig",
    "apps.applications.apps.ApplicationsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.audit.apps.AuditConfig",
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
            ],
        },
    },
]

WSGI_APPLICATION = "e_visa_system.wsgi.application"

# ─── Database — MySQL via PyMySQL ─────────────────────────────────────────────
# All credentials come from environment variables; no secrets are hardcoded.
# utf8mb4  ─ full Unicode support (emoji, supplementary CJK, etc.)
# STRICT_TRANS_TABLES ─ MySQL rejects bad data; no silent coercion.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": _env("DB_NAME", required=True),
        "USER": _env("DB_USER", required=True),
        "PASSWORD": _env("DB_PASSWORD", default=""),
        "HOST": _env("DB_HOST", default="127.0.0.1"),
        "PORT": _env("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "sql_mode": "STRICT_TRANS_TABLES",
        },
    }
}

# ─── Custom user model ───────────────────────────────────────────────────────
# Points to the UUID-based, email-authenticated model in the accounts app.
AUTH_USER_MODEL = "accounts.User"

# ─── Default primary-key type ────────────────────────────────────────────────
# BigAutoField for high-growth tables (audit logs, documents, payments).
# UUID PKs are declared explicitly on externally-visible models.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Password validation ─────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internationalisation ────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── Static files ────────────────────────────────────────────────────────────
STATIC_URL = "static/"

"""Base settings shared by all environments."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "cloudinary_storage",
    "cloudinary",
]

LOCAL_APPS = [
    "common.apps.CommonConfig",
    "accounts",
    "futsal",
    "bookings",
    "payments",
    "notifications",
    "dashboard",
    "contact",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# Database.
# Prefer a single DATABASE_URL when present (Docker/hosting platforms usually
# inject one); otherwise fall back to discrete DB_* variables.
DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="futsal"),
            "USER": config("DB_USER", default="postgres"),
            "PASSWORD": config("DB_PASSWORD", default="postgres"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
            "CONN_MAX_AGE": 600,
        }
    }

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "common.validators.StrongPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="Asia/Kathmandu")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Cloudinary (images & videos) -----------------------------------------
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")
USE_CLOUDINARY = config(
    "USE_CLOUDINARY",
    default=bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET),
    cast=bool,
)
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
    "SECURE": True,
    "PREFIX": config("CLOUDINARY_FOLDER", default="futsal"),
    "MAGIC_FILE_PATH": "magic",
    "INVALID_VIDEO_ERROR_MESSAGE": "Please upload a valid video file.",
}
# Shared secret for the HTTP cron endpoint. Empty means it rejects every request.
CRON_SECRET = config("CRON_SECRET", default="")
MAX_IMAGE_UPLOAD_MB = config("MAX_IMAGE_UPLOAD_MB", default=5, cast=int)
MAX_VIDEO_UPLOAD_MB = config("MAX_VIDEO_UPLOAD_MB", default=100, cast=int)
STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "EXCEPTION_HANDLER": "common.exception_handlers.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "login": config("THROTTLE_LOGIN", default="10/min"),
        "otp": config("THROTTLE_OTP", default="5/min"),
        "register": config("THROTTLE_REGISTER", default="10/hour"),
        "contact": config("THROTTLE_CONTACT", default="10/hour"),
        "anon": "100/min",
        "user": "1000/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME", default=15, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME", default=7, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Futsal Management System API",
    "DESCRIPTION": "REST API for futsal venue, slot, booking, payment and reminder management.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "ENUM_NAME_OVERRIDES": {
        "SlotStatusEnum": "common.enums.SlotStatus.choices",
        "RoleEnum": "common.enums.UserRole.choices",
        "BookingStatusEnum": "common.enums.BookingStatus.choices",
        "PaymentStatusEnum": "common.enums.PaymentStatus.choices",
        "ContactStatusEnum": "common.enums.ContactStatus.choices",
        "FutsalStatusEnum": "common.enums.FutsalStatus.choices",
        "ReminderStatusEnum": "common.enums.ReminderStatus.choices",
    },
    "TAGS": [
        {"name": "auth", "description": "Registration, OTP, login, tokens, passwords"},
        {"name": "users", "description": "User profile"},
        {"name": "futsal", "description": "Futsal details (single venue)"},
        {"name": "slots", "description": "Date-wise slot availability (read-only)"},
        {"name": "bookings", "description": "User bookings, cancel and reschedule"},
        {"name": "contact", "description": "Contact us"},
        {"name": "admin-profile", "description": "Admin profile and password"},
        {"name": "admin-futsal", "description": "Futsal configuration (pricing, hours)"},
        {"name": "admin-slots", "description": "Slot management and bulk generation"},
        {"name": "admin-bookings", "description": "Booking management, cancel, reschedule, complete"},
        {"name": "admin-notifications", "description": "In-app booking notifications for administrators"},
        {"name": "analytics", "description": "Analytics dashboard reporting"},
        {"name": "dashboard", "description": "Today's operational dashboard"},
        {"name": "admin-contact", "description": "Contact message triage"},
        {"name": "admin-reminders", "description": "Reminder history and manual sending"},
        {"name": "admin-media", "description": "Futsal image/video uploads (Cloudinary)"},
        {"name": "internal", "description": "Internal cron/scheduler endpoints"},
    ],
}

# --- Email -----------------------------------------------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@futsal.local")

# --- Celery ----------------------------------------------------------------
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# --- CORS ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="http://localhost:3000", cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# --- Business configuration ------------------------------------------------
OTP_EXPIRY_MINUTES = config("OTP_EXPIRY_MINUTES", default=10, cast=int)
OTP_MAX_ATTEMPTS = config("OTP_MAX_ATTEMPTS", default=5, cast=int)
OTP_RESEND_COOLDOWN_SECONDS = config("OTP_RESEND_COOLDOWN_SECONDS", default=60, cast=int)
OTP_MAX_PER_HOUR = config("OTP_MAX_PER_HOUR", default=5, cast=int)
BOOKING_REFERENCE_PREFIX = config("BOOKING_REFERENCE_PREFIX", default="FSL")
REMINDER_LEAD_MINUTES = config("REMINDER_LEAD_MINUTES", default=60, cast=int)
REMINDER_WINDOW_MINUTES = config("REMINDER_WINDOW_MINUTES", default=10, cast=int)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(process)d %(message)s",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": config("LOG_LEVEL", default="INFO")},
    "loggers": {
        "futsal": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.db.backends": {"level": "WARNING"},
    },
}

# MongoDB is an optional, structured log store.  It is enabled only when a
# connection URI is supplied, keeping local development free of external I/O.
if config("MONGODB_LOG_URI", default=""):
    LOGGING["handlers"]["mongodb"] = {
        "class": "common.mongo_logging.MongoDBHandler",
        "uri": config("MONGODB_LOG_URI"),
        "database": config("MONGODB_LOG_DATABASE", default="futsal_logs"),
        "collection": config("MONGODB_LOG_COLLECTION", default="application_logs"),
        "environment": config("LOG_ENVIRONMENT", default="production"),
        "level": config("MONGODB_LOG_LEVEL", default="INFO"),
    }
    LOGGING["root"]["handlers"].append("mongodb")
    LOGGING["loggers"]["futsal"]["handlers"].append("mongodb")

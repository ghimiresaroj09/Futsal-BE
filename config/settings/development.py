"""Development settings."""
from .base import *  # noqa: F401,F403
from .base import config

DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
CORS_ALLOW_ALL_ORIGINS = True
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

"""Test settings: sqlite + locmem email + eager celery, so the suite runs anywhere."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR

DEBUG = False
# Tests must never require Cloudinary credentials or make network uploads.
USE_CLOUDINARY = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
        "TEST": {"NAME": BASE_DIR / "test_db.sqlite3"},
    }
}
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {  # noqa: F405
    "login": "1000/min", "otp": "1000/min", "register": "1000/min",
    "contact": "1000/min", "anon": "1000/min", "user": "10000/hour",
}}

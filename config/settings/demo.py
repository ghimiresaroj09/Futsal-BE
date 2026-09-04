"""Local demo settings: SQLite + console email, for browsing the API docs without Postgres."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, config

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*.e2b.app"]
CORS_ALLOW_ALL_ORIGINS = True
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "demo.sqlite3"}}
EMAIL_BACKEND = config(
	"EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

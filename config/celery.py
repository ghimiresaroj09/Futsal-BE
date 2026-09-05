"""Celery application and beat schedule."""
from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("futsal")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "dispatch-due-reminders": {
        "task": "notifications.dispatch_due_reminders",
        "schedule": crontab(minute="*/5"),
    },
    "complete-expired-bookings": {
        "task": "bookings.complete_expired_bookings",
        "schedule": crontab(minute="*/5"),
    },
}


@app.task(bind=True)
def debug_task(self):  # pragma: no cover
    print(f"Request: {self.request!r}")

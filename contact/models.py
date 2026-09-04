"""Contact-us messages."""
from __future__ import annotations

from django.db import models

from common.enums import ContactStatus
from common.models import BaseModel
from common.validators import validate_phone_number


class ContactMessage(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=ContactStatus.choices,
                              default=ContactStatus.NEW, db_index=True)
    admin_notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "contact_message"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} ({self.email})"

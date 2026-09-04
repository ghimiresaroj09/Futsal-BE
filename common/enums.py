"""Project-wide choices."""
from django.db import models


class UserRole(models.TextChoices):
    USER = "USER", "User"
    ADMIN = "ADMIN", "Admin"


class OTPPurpose(models.TextChoices):
    REGISTRATION = "REGISTRATION", "Registration"
    FORGOT_PASSWORD = "FORGOT_PASSWORD", "Forgot password"


class SlotStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    BOOKED = "BOOKED", "Booked"
    BLOCKED = "BLOCKED", "Blocked"


class BookingStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    CANCELLED = "CANCELLED", "Cancelled"
    COMPLETED = "COMPLETED", "Completed"
    RESCHEDULED = "RESCHEDULED", "Rescheduled"


class BookingSource(models.TextChoices):
    USER = "USER", "User"
    ADMIN = "ADMIN", "Admin"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    CARD = "CARD", "Card"
    ESEWA = "ESEWA", "eSewa"
    KHALTI = "KHALTI", "Khalti"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank transfer"


class ReminderType(models.TextChoices):
    AUTOMATIC_ONE_HOUR = "AUTOMATIC_ONE_HOUR", "Automatic one hour"
    MANUAL = "MANUAL", "Manual"


class ReminderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"


class ContactStatus(models.TextChoices):
    NEW = "NEW", "New"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    RESOLVED = "RESOLVED", "Resolved"


class FutsalStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"

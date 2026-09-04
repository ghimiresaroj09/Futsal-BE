"""Custom domain exceptions mapped to consistent API errors."""
from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class ServiceError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Request could not be processed."
    default_code = "service_error"

    def __init__(self, detail=None, errors=None, code=None):
        super().__init__(detail or self.default_detail, code)
        self.errors = errors or {}


class ConflictError(ServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflicting request."
    default_code = "conflict"


class SlotUnavailableError(ConflictError):
    default_detail = "Slot is already booked."
    default_code = "slot_unavailable"


class InvalidStateTransition(ServiceError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "This state transition is not allowed."
    default_code = "invalid_transition"


class RateLimitedError(ServiceError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Too many requests. Please try again later."
    default_code = "rate_limited"


class EmailDeliveryError(ServiceError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Email could not be delivered."
    default_code = "email_delivery_failed"

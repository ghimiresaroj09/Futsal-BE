"""Centralised DRF exception handling producing the standard error envelope."""
from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from common.exceptions import ServiceError

logger = logging.getLogger("futsal.errors")

_DEFAULT_MESSAGES = {
    status.HTTP_401_UNAUTHORIZED: "Authentication credentials were not provided or are invalid.",
    status.HTTP_403_FORBIDDEN: "You do not have permission to perform this action.",
    status.HTTP_404_NOT_FOUND: "Resource not found.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Method not allowed.",
    status.HTTP_429_TOO_MANY_REQUESTS: "Too many requests. Please try again later.",
}


def _flatten_message(detail) -> str:
    if isinstance(detail, dict):
        for value in detail.values():
            return _flatten_message(value)
    if isinstance(detail, (list, tuple)) and detail:
        return _flatten_message(detail[0])
    return str(detail)


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail=getattr(exc, "message_dict", exc.messages))
    if isinstance(exc, Http404):
        exc = APIException(detail="Resource not found.")
        exc.status_code = status.HTTP_404_NOT_FOUND
    if isinstance(exc, PermissionDenied):
        exc = APIException(detail="You do not have permission to perform this action.")
        exc.status_code = status.HTTP_403_FORBIDDEN

    response = drf_exception_handler(exc, context)

    if response is None:
        if isinstance(exc, IntegrityError):
            logger.warning("Integrity error: %s", exc)
            return Response(
                {
                    "success": False,
                    "message": "Conflicting request.",
                    "errors": {"detail": ["The resource is in a conflicting state."]},
                },
                status=status.HTTP_409_CONFLICT,
            )
        logger.exception("Unhandled exception", exc_info=exc)
        return Response(
            {
                "success": False,
                "message": "Internal server error.",
                "errors": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data
    errors: dict = {}
    if isinstance(exc, ValidationError):
        message = "Validation failed."
        errors = detail if isinstance(detail, dict) else {"detail": detail}
    else:
        message = _DEFAULT_MESSAGES.get(response.status_code) or _flatten_message(detail)
        if isinstance(exc, (APIException,)) and not isinstance(detail, dict):
            message = _flatten_message(detail)
        errors = getattr(exc, "errors", None) or (
            detail if isinstance(detail, dict) else {"detail": [_flatten_message(detail)]}
        )
    if isinstance(exc, ServiceError):
        message = _flatten_message(exc.detail)

    response.data = {"success": False, "message": message, "errors": errors}
    return response

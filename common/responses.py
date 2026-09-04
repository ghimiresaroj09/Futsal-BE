"""Standard API envelope helpers."""
from __future__ import annotations

from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response


def success_response(
    data: Any = None, message: str = "Success", status: int = http_status.HTTP_200_OK
) -> Response:
    return Response(
        {"success": True, "message": message, "data": data if data is not None else {}},
        status=status,
    )


def error_response(
    message: str = "Request failed",
    errors: dict | None = None,
    status: int = http_status.HTTP_400_BAD_REQUEST,
) -> Response:
    return Response(
        {"success": False, "message": message, "errors": errors or {}}, status=status
    )

"""Health check endpoint for platform probes."""
from __future__ import annotations

import logging

from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("futsal.health")


class HealthView(APIView):
    """Liveness/readiness probe. Returns 200 when the app can serve traffic."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["internal"],
        summary="Health check",
        description="Returns 200 when the application and database are reachable.",
        responses={
            200: OpenApiResponse(description="Service healthy."),
            503: OpenApiResponse(description="Database unreachable."),
        },
    )
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as exc:  # noqa: BLE001
            logger.error("Health check failed: %s", exc)
            return Response(
                {
                    "success": False,
                    "message": "Service unhealthy.",
                    "errors": {"database": ["Database connection failed."]},
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "success": True,
                "message": "Service healthy.",
                "data": {"status": "ok", "database": "ok"},
            },
            status=status.HTTP_200_OK,
        )

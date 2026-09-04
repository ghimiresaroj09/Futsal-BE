"""HTTP cron endpoint for scheduled reminder dispatch."""
from __future__ import annotations

import hmac
import logging

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.responses import success_response

logger = logging.getLogger("futsal.cron")


class CronReminderView(APIView):
    """Dispatch due booking reminders. Called by an external scheduler."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def _authorised(self, request) -> bool:
        secret = getattr(settings, "CRON_SECRET", "")
        if not secret:
            return False
        provided = request.headers.get("Authorization", "")
        return hmac.compare_digest(provided, f"Bearer {secret}")

    @extend_schema(
        tags=["internal"],
        summary="Cron: dispatch due booking reminders",
        description=(
            "Replaces Celery Beat where no scheduler process can run. Requires the "
            "`Authorization: Bearer <CRON_SECRET>` header."
        ),
        responses={
            200: OpenApiResponse(description="Reminders dispatched."),
            401: OpenApiResponse(description="Missing or invalid cron secret."),
        },
    )
    def get(self, request):
        if not self._authorised(request):
            logger.warning("Rejected unauthorised cron request")
            return Response(
                {
                    "success": False,
                    "message": "Unauthorised.",
                    "errors": {"detail": ["Invalid cron credentials."]},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from notifications.services import (
            send_automatic_reminder,
            upcoming_bookings_needing_reminder,
        )

        sent = failed = 0
        for booking in upcoming_bookings_needing_reminder():
            try:
                if send_automatic_reminder(booking=booking) is not None:
                    sent += 1
            except Exception:  # noqa: BLE001
                failed += 1
                logger.exception("Reminder failed for booking %s", booking.pk)

        logger.info("cron reminders sent=%d failed=%d", sent, failed)
        return success_response(
            data={"sent": sent, "failed": failed},
            message="Reminder dispatch completed.",
        )

    @extend_schema(
        tags=["internal"],
        summary="Cron: dispatch due booking reminders (POST alias)",
        request=None,
        responses={
            200: OpenApiResponse(description="Reminders dispatched."),
            401: OpenApiResponse(description="Missing or invalid cron secret."),
        },
    )
    def post(self, request):
        return self.get(request)

"""HTTP cron endpoint for scheduled reminder dispatch.

On hosts where no Celery Beat process can run (free-tier PaaS, serverless), the
periodic reminder dispatch is exposed as an HTTP endpoint that an external
scheduler calls. The work itself is unchanged: this calls the very same service
functions the Celery task calls, so behaviour is identical either way.

Security: the endpoint is public-facing, so it is protected by a shared secret.
Schedulers send ``Authorization: Bearer $CRON_SECRET``. Set the
CRON_SECRET environment variable on the service.
"""
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
            # Fail closed: without a configured secret the endpoint stays shut.
            return False
        provided = request.headers.get("Authorization", "")
        expected = f"Bearer {secret}"
        # Constant-time compare so the secret cannot be guessed by timing.
        return hmac.compare_digest(provided, expected)

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

        # Imported lazily so a missing Celery broker never blocks the import.
        try:
            from notifications.services import (
                send_automatic_reminder, upcoming_bookings_needing_reminder,
            )
        except Exception as exc:  # noqa: BLE001 - import-time failure must not 500 the scheduler
            logger.exception("Cron reminder import failed")
            return self._degraded("import_failed", exc)

        # Selecting candidates is a single query over booking/slot rows. A bad row
        # or a data-shape problem here must not take down the whole endpoint,
        # otherwise the scheduler sees an opaque 500 and keep-alive stops working.
        try:
            candidates = list(upcoming_bookings_needing_reminder())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Cron reminder candidate query failed")
            return self._degraded("candidate_query_failed", exc)

        sent = 0
        failed = 0
        for booking in candidates:
            try:
                if send_automatic_reminder(booking=booking) is not None:
                    sent += 1
            except Exception:  # noqa: BLE001 - one bad booking must not stop the run
                failed += 1
                logger.exception("Reminder failed for booking %s", booking.pk)

        logger.info("cron reminders sent=%d failed=%d", sent, failed)
        return success_response(
            data={"sent": sent, "failed": failed},
            message="Reminder dispatch completed.",
        )

    def _degraded(self, stage: str, exc: Exception) -> Response:
        """Return 200 with an error payload instead of a 500.

        The caller is already authenticated with the shared secret, so echoing the
        exception type/message is safe and is the only practical way to diagnose a
        failure on a host where DEBUG is off and logs may be unavailable. Status
        stays 200 so the scheduler keeps calling (and keeps the instance warm)
        rather than disabling the job after repeated failures.
        """
        return success_response(
            data={
                "sent": 0,
                "failed": 0,
                "error": {
                    "stage": stage,
                    "type": type(exc).__name__,
                    "detail": str(exc)[:500],
                },
            },
            message="Reminder dispatch degraded.",
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
        """Schedulers issue GET; POST is allowed for manual curl triggers."""
        return self.get(request)

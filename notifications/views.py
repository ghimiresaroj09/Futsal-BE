"""Admin reminder APIs."""
from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from notifications.models import Reminder
from notifications.serializers import ReminderSerializer


@extend_schema(tags=["admin-reminders"], summary="Reminder history (automatic and manual)")
class AdminReminderViewSet(EnvelopeMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ["status", "reminder_type", "booking"]
    search_fields = ["booking__booking_reference", "booking__email"]
    ordering_fields = ["created_at", "scheduled_at", "sent_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Reminder.objects.select_related("booking")

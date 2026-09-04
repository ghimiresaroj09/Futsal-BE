"""Admin reminder APIs."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from notifications.models import AdminNotification, Reminder
from notifications.serializers import (
    AdminNotificationActionSerializer, AdminNotificationSerializer,
    AdminNotificationListSerializer, MarkAllNotificationsReadSerializer,
    ReminderSerializer,
)


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


@extend_schema(tags=["admin-notifications"], summary="Admin in-app booking notifications")
class AdminNotificationViewSet(EnvelopeMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):
    """Notifications belonging only to the authenticated administrator."""

    serializer_class = AdminNotificationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AdminNotification.objects.all()
    # Notifications are always presented newest first; only the read-state
    # parameters handled below are accepted as list filters.
    filter_backends = []

    def unread_count(self) -> int:
        return AdminNotification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()

    def notification_response(self, notification):
        data = AdminNotificationActionSerializer(notification).data
        data["unread_count"] = self.unread_count()
        return Response(data)

    def get_queryset(self):
        queryset = AdminNotification.objects.filter(recipient=self.request.user).select_related("booking")
        read = self.request.query_params.get("read")
        if read in {"read", "true", "1"}:
            queryset = queryset.filter(is_read=True)
        elif read in {"unread", "false", "0"}:
            queryset = queryset.filter(is_read=False)
        elif "is_read" in self.request.query_params:
            value = self.request.query_params["is_read"].lower()
            if value in {"true", "1"}:
                queryset = queryset.filter(is_read=True)
            elif value in {"false", "0"}:
                queryset = queryset.filter(is_read=False)
        return queryset.order_by("-created_at")

    @extend_schema(
        summary="List booking notifications",
        description=(
            "Returns only the current admin's in-app notifications, newest first. "
            "`unread_count` is the total unread count before any read-state filter."
        ),
        parameters=[
            OpenApiParameter(
                "read", OpenApiTypes.STR, OpenApiParameter.QUERY,
                description="Optional state filter: `read` or `unread` (also accepts true/false).",
                enum=["read", "unread"],
            ),
            OpenApiParameter(
                "is_read", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                description="Boolean alias for the `read` filter.",
            ),
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses=AdminNotificationListSerializer,
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["unread_count"] = self.unread_count()
        return response

    @extend_schema(
        summary="Mark one notification as read",
        description="Marks a notification owned by the current admin as read and returns the updated unread badge count.",
        request=None,
        responses=AdminNotificationActionSerializer,
    )
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return self.notification_response(notification)

    @extend_schema(
        summary="Mark one notification as unread",
        description="Marks a notification owned by the current admin as unread and returns the updated unread badge count.",
        request=None,
        responses=AdminNotificationActionSerializer,
    )
    @action(detail=True, methods=["post"], url_path="mark-unread")
    def mark_unread(self, request, pk=None):
        notification = self.get_object()
        if notification.is_read or notification.read_at is not None:
            notification.is_read = False
            notification.read_at = None
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return self.notification_response(notification)

    @extend_schema(
        summary="Mark all notifications as read",
        description="Marks every unread notification for the current admin as read.",
        request=None,
        responses=MarkAllNotificationsReadSerializer,
    )
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({
            "marked_as_read": updated,
            "unread_count": self.unread_count(),
        }, status=status.HTTP_200_OK)

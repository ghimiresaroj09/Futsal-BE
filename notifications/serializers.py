import datetime as dt

from django.utils import timezone
from django.utils.timesince import timesince
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from notifications.models import AdminNotification, Reminder


class ReminderSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source="booking.booking_reference",
                                              read_only=True)

    class Meta:
        model = Reminder
        fields = ["id", "booking", "booking_reference", "reminder_type", "scheduled_at",
                  "sent_at", "status", "error_message", "created_at"]
        read_only_fields = fields


class AdminNotificationSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source="booking.booking_reference", read_only=True)
    time_ago = serializers.SerializerMethodField()
    redirect_url = serializers.SerializerMethodField()

    class Meta:
        model = AdminNotification
        fields = [
            "id", "booking", "booking_reference", "title", "message", "is_read",
            "read_at", "created_at", "time_ago", "redirect_url",
        ]
        read_only_fields = fields

    def get_time_ago(self, obj) -> str:
        if obj.created_at >= timezone.now() - dt.timedelta(minutes=1):
            return "just now"
        return f"{timesince(obj.created_at, timezone.now())} ago"

    def get_redirect_url(self, obj) -> str:
        """Frontend route for opening the booking that caused this notification."""
        return f"/admin/bookings/{obj.booking_id}"


class AdminNotificationActionSerializer(AdminNotificationSerializer):
    """Notification returned by a read-state action, with bell badge count."""

    unread_count = serializers.IntegerField(read_only=True)

    class Meta(AdminNotificationSerializer.Meta):
        fields = [*AdminNotificationSerializer.Meta.fields, "unread_count"]


class MarkAllNotificationsReadSerializer(serializers.Serializer):
    marked_as_read = serializers.IntegerField(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)


@extend_schema_serializer(many=False)
class AdminNotificationListSerializer(serializers.Serializer):
    """The paginated notification data returned by the list endpoint."""

    count = serializers.IntegerField(read_only=True)
    next = serializers.URLField(read_only=True, allow_null=True)
    previous = serializers.URLField(read_only=True, allow_null=True)
    results = AdminNotificationSerializer(many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)

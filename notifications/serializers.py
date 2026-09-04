from rest_framework import serializers

from notifications.models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source="booking.booking_reference",
                                              read_only=True)

    class Meta:
        model = Reminder
        fields = ["id", "booking", "booking_reference", "reminder_type", "scheduled_at",
                  "sent_at", "status", "error_message", "created_at"]
        read_only_fields = fields

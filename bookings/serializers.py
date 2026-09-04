"""Booking serializers."""
from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from bookings.models import Booking
from common.enums import BookingStatus, PaymentMethod
from common.validators import validate_full_name, validate_phone_number
from futsal.serializers import SlotSerializer


class BookingSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(read_only=True)
    futsal_name = serializers.CharField(source="futsal.name", read_only=True)
    payment_status = serializers.CharField(source="payment.payment_status", read_only=True,
                                           default=None)

    class Meta:
        model = Booking
        fields = [
            "id", "booking_reference", "slot", "futsal_name", "full_name",
            "email", "phone_number", "amount", "status", "booking_source", "payment_status",
            "cancelled_at", "cancellation_reason", "notes", "created_at", "updated_at",
        ]
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    slot_id = serializers.UUIDField()
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_full_name(self, value):
        try:
            return validate_full_name(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_phone_number(self, value):
        try:
            return validate_phone_number(value.strip())
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))


class BookingUpdateSerializer(serializers.Serializer):
    """User-editable booking contact details."""

    full_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_full_name(self, value):
        try:
            return validate_full_name(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_phone_number(self, value):
        try:
            return validate_phone_number(value.strip())
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=[*validated_data.keys(), "updated_at"])
        return instance


class AdminBookingCreateSerializer(BookingCreateSerializer):
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices,
                                             default=PaymentMethod.CASH)
    status = serializers.ChoiceField(
        choices=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        default=BookingStatus.CONFIRMED,
    )


class RescheduleSerializer(serializers.Serializer):
    new_slot_id = serializers.UUIDField()


class CancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="",
                                   max_length=255)


class AdminBookingUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BookingStatus.choices, required=False)
    full_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)

"""Futsal and slot serializers."""
from __future__ import annotations

import datetime as dt

from django.db.models import Q
from rest_framework import serializers

from common.enums import SlotStatus
from common.utils import local_today
from futsal.models import Futsal, FutsalClosure, FutsalMedia, Slot


class SlotGenerateSerializer(serializers.Serializer):
    """Generate whole-hour slots for a date range from the futsal opening hours."""

    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start = attrs["start_date"]
        end = attrs.get("end_date") or start
        if end < start:
            raise serializers.ValidationError(
                {"end_date": ["End date must be on or after start date."]}
            )
        if start < local_today():
            raise serializers.ValidationError(
                {"start_date": ["Start date cannot be in the past."]}
            )
        if (end - start).days > 90:
            raise serializers.ValidationError(
                {"end_date": ["Cannot generate more than 90 days at a time."]}
            )
        attrs["end_date"] = end
        return attrs


class SlotDateSerializer(serializers.Serializer):
    date = serializers.DateField()


class BulkSlotItemSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    status = serializers.ChoiceField(
        choices=[SlotStatus.AVAILABLE, SlotStatus.BLOCKED], required=False
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, allow_null=True
    )

    def validate(self, attrs):
        if "status" not in attrs and "price" not in attrs:
            raise serializers.ValidationError("Provide status or price for this slot.")
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]
        if start_time.minute or start_time.second or start_time.microsecond:
            raise serializers.ValidationError("start_time must be on the hour, e.g. 19:00.")
        if end_time.minute or end_time.second or end_time.microsecond:
            raise serializers.ValidationError("end_time must be on the hour, e.g. 20:00.")
        if end_time <= start_time:
            raise serializers.ValidationError("end_time must be after start_time.")
        duration = (
            dt.datetime.combine(dt.date.min, end_time)
            - dt.datetime.combine(dt.date.min, start_time)
        )
        if duration != dt.timedelta(hours=1):
            raise serializers.ValidationError("A slot must be exactly one hour long.")
        return attrs


class BulkSlotUpdateSerializer(serializers.Serializer):
    date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=[SlotStatus.AVAILABLE, SlotStatus.BLOCKED], required=False
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, required=False, allow_null=True
    )
    slots = BulkSlotItemSerializer(many=True, required=False)

    def validate(self, attrs):
        if "slots" not in attrs and "status" not in attrs and "price" not in attrs:
            raise serializers.ValidationError(
                "Provide status, price, or a slots list with per-slot updates."
            )
        return attrs


class SlotCopyNextDaySerializer(serializers.Serializer):
    """Copy the previous day's slot layout into the requested date."""

    date = serializers.DateField(help_text="Target date; slots are copied from the previous day.")

    def validate_date(self, value: dt.date) -> dt.date:
        if value < local_today():
            raise serializers.ValidationError("Target date cannot be in the past.")
        return value


class BlockDaySerializer(serializers.Serializer):
    """Close the futsal for one whole day."""

    date = serializers.DateField()
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True,
                                   default="")
    cancel_bookings = serializers.BooleanField(
        default=False,
        help_text="Cancel and refund any existing bookings on this date.",
    )

    def validate_date(self, value: dt.date) -> dt.date:
        if value < local_today():
            raise serializers.ValidationError("Cannot block a date in the past.")
        return value


class BlockDayRangeSerializer(serializers.Serializer):
    """Close the futsal for a range of days."""

    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True,
                                   default="")
    cancel_bookings = serializers.BooleanField(default=False)

    def validate(self, attrs):
        start = attrs["start_date"]
        end = attrs.get("end_date") or start
        if start < local_today():
            raise serializers.ValidationError(
                {"start_date": ["Cannot block a date in the past."]}
            )
        if end < start:
            raise serializers.ValidationError(
                {"end_date": ["End date must be on or after start date."]}
            )
        if (end - start).days > 90:
            raise serializers.ValidationError(
                {"end_date": ["Cannot block more than 90 days at a time."]}
            )
        attrs["end_date"] = end
        return attrs


class UnblockDaySerializer(serializers.Serializer):
    date = serializers.DateField()


class FutsalClosureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FutsalClosure
        fields = ["id", "date", "reason", "created_at"]
        read_only_fields = fields


class FutsalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Futsal
        fields = [
            "id", "name", "description", "location", "address", "phone", "email",
            "price_per_slot", "slot_duration", "opening_time", "closing_time", "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        opening = attrs.get("opening_time", getattr(self.instance, "opening_time", None))
        closing = attrs.get("closing_time", getattr(self.instance, "closing_time", None))
        if opening and closing and opening >= closing:
            raise serializers.ValidationError(
                {"closing_time": ["Closing time must be after opening time."]}
            )
        return attrs


class SlotSerializer(serializers.ModelSerializer):
    """Public/read representation of a slot."""

    price = serializers.DecimalField(source="effective_price", max_digits=10,
                                     decimal_places=2, read_only=True)

    class Meta:
        model = Slot
        fields = ["id", "date", "start_time", "end_time", "price", "status",
                  "created_at", "updated_at"]
        read_only_fields = fields


class SlotWriteSerializer(serializers.ModelSerializer):
    """Admin slot create/update.

    The futsal is implicit (single-venue system) and slots run on whole hours,
    e.g. 07:00 - 08:00.
    """

    class Meta:
        model = Slot
        fields = ["id", "date", "start_time", "end_time", "price", "status"]
        read_only_fields = ["id"]

    def validate_date(self, value: dt.date) -> dt.date:
        if self.instance is None and value < local_today():
            raise serializers.ValidationError("Slot date cannot be in the past.")
        return value

    @staticmethod
    def _assert_whole_hour(field: str, value: dt.time) -> None:
        if value.minute or value.second or value.microsecond:
            raise serializers.ValidationError(
                {field: ["Time must be on the hour, e.g. 07:00."]}
            )

    def validate_status(self, value: str) -> str:
        if self.instance and self.instance.status == SlotStatus.BOOKED and value == SlotStatus.BLOCKED:
            raise serializers.ValidationError("A booked slot cannot be blocked.")
        return value

    def validate(self, attrs):
        instance = self.instance
        futsal = Futsal.objects.get_solo()
        date = attrs.get("date", getattr(instance, "date", None))
        start = attrs.get("start_time", getattr(instance, "start_time", None))
        end = attrs.get("end_time", getattr(instance, "end_time", None))
        if start and end and start >= end:
            raise serializers.ValidationError(
                {"end_time": ["End time must be after start time."]}
            )
        self._assert_whole_hour("start_time", start)
        self._assert_whole_hour("end_time", end)
        if start and end:
            duration = (
                dt.datetime.combine(dt.date.min, end) - dt.datetime.combine(dt.date.min, start)
            )
            if duration != dt.timedelta(hours=1):
                raise serializers.ValidationError(
                    {"end_time": ["A slot must be exactly one hour long."]}
                )
        if date and start and end:
            overlapping = Slot.objects.filter(
                futsal=futsal, date=date
            ).filter(Q(start_time__lt=end) & Q(end_time__gt=start))
            if instance is not None:
                overlapping = overlapping.exclude(pk=instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError(
                    {"start_time": ["This slot overlaps an existing slot."]}
                )
        return attrs


class FutsalMediaSerializer(serializers.ModelSerializer):
    """Read representation of a gallery item."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = FutsalMedia
        fields = ["id", "media_type", "url", "caption", "is_cover", "sort_order", "created_at"]
        read_only_fields = fields

    def get_url(self, obj) -> str | None:
        return obj.url


class FutsalMediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FutsalMedia
        fields = ["id", "media_type", "image", "video", "caption", "is_cover", "sort_order"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        media_type = attrs.get(
            "media_type",
            self.instance.media_type if self.instance else FutsalMedia.MediaType.IMAGE,
        )
        image = attrs.get("image")
        video = attrs.get("video")
        if image and video:
            raise serializers.ValidationError({"video": ["Provide either an image or a video, not both."]})
        if media_type == FutsalMedia.MediaType.IMAGE and video:
            raise serializers.ValidationError({"video": ["A video cannot be used when media_type is IMAGE."]})
        if media_type == FutsalMedia.MediaType.VIDEO and image:
            raise serializers.ValidationError({"image": ["An image cannot be used when media_type is VIDEO."]})
        if not self.instance and media_type == FutsalMedia.MediaType.IMAGE and not image:
            raise serializers.ValidationError({"image": ["An image file is required when media_type is IMAGE."]})
        if not self.instance and media_type == FutsalMedia.MediaType.VIDEO and not video:
            raise serializers.ValidationError({"video": ["A video file is required when media_type is VIDEO."]})
        if self.instance and "media_type" in attrs and media_type != self.instance.media_type:
            required_file = image if media_type == FutsalMedia.MediaType.IMAGE else video
            if not required_file:
                raise serializers.ValidationError(
                    {"image" if media_type == FutsalMedia.MediaType.IMAGE else "video":
                     ["A matching file is required when changing media_type."]}
                )
        attrs["media_type"] = media_type
        return attrs

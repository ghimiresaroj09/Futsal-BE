"""Public futsal/slot APIs and admin slot management (single-venue system)."""
from __future__ import annotations

import datetime as dt

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response  # <-- ADD THIS IMPORT ONLY

from common.enums import SlotStatus
from common.exceptions import ConflictError
from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.responses import success_response
from futsal.filters import SlotFilter
from futsal.models import Futsal, FutsalMedia
from futsal.selectors import slots_queryset
from futsal.services import (
    block_day,
    bulk_update_named_slots,
    bulk_update_slots_for_date,
    copy_slots_to_next_day,
    generate_slots_for_range,
    unblock_day,
)
from futsal.models import FutsalClosure
from futsal.serializers import (
    BlockDayRangeSerializer, BlockDaySerializer, FutsalClosureSerializer, FutsalSerializer,
    SlotGenerateSerializer, SlotSerializer, SlotWriteSerializer, UnblockDaySerializer,
    SlotCopyNextDaySerializer, SlotDateSerializer, BulkSlotUpdateSerializer,
    FutsalMediaSerializer, FutsalMediaUploadSerializer,
)
from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view, inline_serializer,
)
from rest_framework import serializers, status, viewsets


@extend_schema(tags=["futsal"], summary="Futsal details (single venue)")
class FutsalDetailView(GenericAPIView):
    """Public read of the one configured futsal."""

    serializer_class = FutsalSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        futsal = Futsal.objects.get_solo()
        return success_response(data=FutsalSerializer(futsal).data,
                                message="Futsal retrieved successfully.")


@extend_schema(tags=["admin-futsal"], summary="View or update the futsal configuration")
class AdminFutsalView(GenericAPIView):
    """Admin read/update of the single futsal. Creation/deletion is not supported."""

    serializer_class = FutsalSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return success_response(data=FutsalSerializer(Futsal.objects.get_solo()).data,
                                message="Futsal retrieved successfully.")

    def patch(self, request):
        futsal = Futsal.objects.get_solo()
        serializer = self.get_serializer(futsal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data,
                                message="Futsal updated successfully.")


@extend_schema_view(
    list=extend_schema(
        tags=["slots"],
        parameters=[OpenApiParameter("date", str, description="Filter by date (YYYY-MM-DD)")],
        summary="List upcoming slots date-wise",
        auth=[],
    ),
    retrieve=extend_schema(tags=["slots"], summary="Retrieve a slot", auth=[]),
)
class PublicSlotViewSet(EnvelopeMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only slot access for users. Users can never modify slots."""

    serializer_class = SlotSerializer
    permission_classes = [AllowAny]
    filterset_class = SlotFilter
    ordering_fields = ["date", "start_time", "created_at"]
    ordering = ["date", "start_time"]

    def get_queryset(self):
        return slots_queryset().upcoming()

    @extend_schema(
        tags=["slots"],
        parameters=[OpenApiParameter("date", str, required=True,
                                     description="Date to retrieve slots for (YYYY-MM-DD)")],
        summary="List slots for a specific date",
        auth=[],
    )
    @action(detail=False, methods=["get"], url_path="date-wise")
    def date_wise(self, request):
        serializer = SlotDateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        queryset = self.get_queryset().filter(date=serializer.validated_data["date"])
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(SlotSerializer(page, many=True).data)


@extend_schema(tags=["admin-slots"])
class AdminSlotViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Admin slot management: whole-hour slots such as 07:00 - 08:00."""

    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_class = SlotFilter
    ordering_fields = ["date", "start_time", "created_at", "status"]
    ordering = ["date", "start_time"]

    def get_queryset(self):
        return slots_queryset()

    def get_serializer_class(self):
        if self.action == "generate":
            return SlotGenerateSerializer
        if self.action == "copy_next_day":
            return SlotCopyNextDaySerializer
        if self.action == "bulk_update":
            return BulkSlotUpdateSerializer
        if self.action == "block_day":
            return BlockDaySerializer
        if self.action == "block_range":
            return BlockDayRangeSerializer
        if self.action == "unblock_day":
            return UnblockDaySerializer
        if self.action == "closures":
            return FutsalClosureSerializer
        if self.action in {"list", "retrieve"}:
            return SlotSerializer
        return SlotWriteSerializer

    @extend_schema(summary="Create a one-hour slot")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = serializer.save(futsal=Futsal.objects.get_solo())
        return success_response(
            data=SlotSerializer(slot).data, message="Slot created successfully.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary="Update a slot")
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        slot = serializer.save()
        return success_response(data=SlotSerializer(slot).data,
                                message="Slot updated successfully.")

    @extend_schema(
        summary="Delete a slot (booked slots cannot be deleted)",
        responses={
            200: inline_serializer(
                name="SlotDeleteResponse",
                fields={
                    "success": serializers.BooleanField(default=True),
                    "message": serializers.CharField(default="Slot deleted successfully."),
                    "data": inline_serializer(
                        name="SlotDeleteData",
                        fields={"id": serializers.UUIDField()},
                    ),
                },
            ),
            409: OpenApiResponse(description="A booked slot cannot be deleted."),
            404: OpenApiResponse(description="Slot not found."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == SlotStatus.BOOKED:
            raise ConflictError("A booked slot cannot be deleted.",
                                errors={"slot": ["A booked slot cannot be deleted."]})
        slot_id = str(instance.id)
        instance.delete()
        # 204 No Content must have an EMPTY body (RFC 9110). Returning the JSON
        # envelope with a 204 makes clients such as Postman fail with
        # "Parse Error: The server returned a malformed response", so use 200.
        return success_response(
            data={"id": slot_id},
            message="Slot deleted successfully.",
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Bulk-generate whole-hour slots for a date range from the opening hours",
    )
    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = generate_slots_for_range(
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
        )
        return success_response(
            data={"created": len(created), "slots": SlotSerializer(created, many=True).data},
            message=f"{len(created)} slot(s) generated successfully.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["admin-slots"],
        summary="Copy the previous day's slots into the requested date",
        description=(
            "Copies start time, end time and custom price from the previous day. "
            "New slots are AVAILABLE and existing target slots are left unchanged."
        ),
    )
    @action(detail=False, methods=["post"], url_path="copy-next-day")
    def copy_next_day(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = copy_slots_to_next_day(
            date=serializer.validated_data["date"],
            futsal=Futsal.objects.get_solo(),
        )
        return success_response(
            data={"created": len(created), "slots": SlotSerializer(created, many=True).data},
            message=f"{len(created)} slot(s) copied successfully.",
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["admin-slots"],
        summary="Bulk-update slots for a date",
        description=(
            "Updates status and/or price for slot pairs on a date. Each per-slot item "
            "must include start_time and end_time. Active booked slots are skipped "
            "for status changes."
        ),
    )
    @action(detail=False, methods=["patch"], url_path="bulk-update")
    def bulk_update(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if "slots" in data:
            result = bulk_update_named_slots(
                date=data["date"], slot_updates=data["slots"], futsal=Futsal.objects.get_solo()
            )
        else:
            result = bulk_update_slots_for_date(
                date=data["date"],
                updates={field: data[field] for field in ("status", "price") if field in data},
                futsal=Futsal.objects.get_solo(),
            )
        result["slots"] = SlotSerializer(result["slots"], many=True).data
        return success_response(data=result, message="Slots updated successfully.")

    @extend_schema(
        tags=["admin-slots"],
        summary="Block an entire day (holiday / maintenance)",
        description=(
            "Marks every AVAILABLE slot on the date as BLOCKED and records a closure so "
            "slot generation will not repopulate the day. Slots with active bookings are "
            "left untouched and reported in `skipped_booked_slots`, unless "
            "`cancel_bookings=true`, which cancels and refunds them first."
        ),
    )
    @action(detail=False, methods=["post"], url_path="block-day")
    def block_day(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        result = block_day(
            date=data["date"], reason=data.get("reason", ""), actor=request.user,
            cancel_bookings=data["cancel_bookings"],
        )
        return success_response(data=result, message="Day blocked successfully.")

    @extend_schema(tags=["admin-slots"], summary="Block a range of days")
    @action(detail=False, methods=["post"], url_path="block-range")
    def block_range(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        results = []
        current = data["start_date"]
        while current <= data["end_date"]:
            results.append(block_day(
                date=current, reason=data.get("reason", ""), actor=request.user,
                cancel_bookings=data["cancel_bookings"],
            ))
            current += dt.timedelta(days=1)
        return success_response(
            data={
                "days_blocked": len(results),
                "blocked_slots": sum(r["blocked_slots"] for r in results),
                "cancelled_bookings": sum(r["cancelled_bookings"] for r in results),
                "skipped_booked_slots": sum(r["skipped_booked_slots"] for r in results),
                "days": results,
            },
            message=f"{len(results)} day(s) blocked successfully.",
        )

    @extend_schema(tags=["admin-slots"], summary="Reopen a blocked day")
    @action(detail=False, methods=["post"], url_path="unblock-day")
    def unblock_day(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = unblock_day(date=serializer.validated_data["date"], actor=request.user)
        return success_response(data=result, message="Day reopened successfully.")

    @extend_schema(tags=["admin-slots"], summary="List closed days")
    @action(detail=False, methods=["get"])
    def closures(self, request):
        queryset = FutsalClosure.objects.all()
        page = self.paginate_queryset(queryset)
        serializer = FutsalClosureSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(tags=["admin-media"])
class AdminFutsalMediaViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Upload and manage gallery assets."""

    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["media_type", "is_cover"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "-created_at"]

    def get_queryset(self):
        return FutsalMedia.objects.select_related("futsal")

    def get_serializer_class(self):
        return FutsalMediaUploadSerializer if self.action in {"create", "update", "partial_update"} else FutsalMediaSerializer

    @extend_schema(summary="Upload an image or video", responses={201: FutsalMediaSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.save(futsal=Futsal.objects.get_solo(), uploaded_by=request.user)
        return success_response(data=FutsalMediaSerializer(media).data,
                                message="Media uploaded successfully.", status=status.HTTP_201_CREATED)

    @extend_schema(summary="Update media metadata", responses={200: FutsalMediaSerializer})
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        media = serializer.save()
        return success_response(data=FutsalMediaSerializer(media).data,
                                message="Media updated successfully.")

    @extend_schema(summary="Delete media and its stored asset")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        media_id = str(instance.id)
        asset = instance.file
        if asset:
            asset.storage.delete(asset.name)
        instance.delete()
        return success_response(data={"id": media_id}, message="Media deleted successfully.",
                                status=status.HTTP_200_OK)


@extend_schema(tags=["futsal"], summary="Public futsal gallery (images and videos)")
class PublicFutsalMediaViewSet(EnvelopeMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FutsalMediaSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["media_type", "is_cover"]
    ordering = ["sort_order", "-created_at"]

    def get_queryset(self):
        return FutsalMedia.objects.select_related("futsal")

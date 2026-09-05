"""User and admin booking APIs."""
from __future__ import annotations

from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import status as http_status
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings import services
from bookings.filters import BookingFilter
from bookings.models import Booking
from bookings.selectors import bookings_queryset
from bookings.serializers import (
    AdminBookingCreateSerializer, AdminBookingUpdateSerializer, BookingCreateSerializer,
    BookingSerializer, BookingUpdateSerializer, CancelSerializer, RescheduleSerializer,
)
from common.enums import BookingSource, BookingStatus
from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.responses import success_response
from notifications.serializers import ReminderSerializer


@extend_schema(tags=["bookings"])
class BookingViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Authenticated users manage only their own bookings."""

    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    filterset_class = BookingFilter
    search_fields = ["booking_reference", "full_name", "email", "phone_number"]
    ordering_fields = ["created_at", "status", "slot__date", "slot__start_time"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Booking.objects.none()
        return bookings_queryset().filter(
            Q(user=user) | Q(booking_source=BookingSource.ADMIN, email__iexact=user.email)
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        if self.action == "reschedule":
            return RescheduleSerializer
        if self.action == "cancel":
            return CancelSerializer
        if self.action in {"update", "partial_update"}:
            return BookingUpdateSerializer
        return BookingSerializer

    @extend_schema(summary="Create a booking (409 if the slot is already booked)")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        booking = services.create_booking(
            slot_id=data["slot_id"],
            full_name=data["full_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            notes=data.get("notes", ""),
            user=request.user,
            created_by=request.user,
            source=BookingSource.USER,
        )
        return success_response(
            data=BookingSerializer(booking).data,
            message="Booking created successfully.",
            status=http_status.HTTP_201_CREATED,
        )

    @extend_schema(summary="Update booking contact details")
    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=BookingSerializer(booking).data,
            message="Booking updated successfully.",
        )

    @extend_schema(summary="Reschedule a booking to a new available slot (atomic)")
    @action(detail=True, methods=["patch"])
    def reschedule(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = services.reschedule_booking(
            booking=booking, new_slot_id=serializer.validated_data["new_slot_id"],
            actor=request.user,
        )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking rescheduled successfully.")

    @extend_schema(summary="Cancel a booking and release the slot")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = services.cancel_booking(
            booking=booking, actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking cancelled successfully.")


@extend_schema(tags=["admin-bookings"])
class AdminBookingViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Full booking management for admins."""

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = BookingSerializer
    filterset_class = BookingFilter
    search_fields = ["booking_reference", "full_name", "email", "phone_number"]
    ordering_fields = ["created_at", "status", "slot__date", "slot__start_time", "amount"]
    ordering = ["slot__date", "slot__start_time"]

    def get_queryset(self):
        return bookings_queryset()

    def get_serializer_class(self):
        if self.action == "create":
            return AdminBookingCreateSerializer
        if self.action in {"update", "partial_update"}:
            return AdminBookingUpdateSerializer
        if self.action == "reschedule":
            return RescheduleSerializer
        return BookingSerializer

    @extend_schema(
        summary="Admin creates a booking on behalf of a customer",
        parameters=[OpenApiParameter("date", str, description="Filter by slot date")],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        booking = services.create_booking(
            slot_id=data["slot_id"],
            full_name=data["full_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            notes=data.get("notes", ""),
            user=None,
            created_by=request.user,
            source=BookingSource.ADMIN,
            payment_method=data.get("payment_method"),
            status=data.get("status", BookingStatus.CONFIRMED),
        )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking created successfully.",
                                status=http_status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        for field in ("full_name", "email", "phone_number", "notes"):
            if field in data:
                setattr(booking, field, data[field])
        booking.save()
        if "status" in data:
            booking = services.change_booking_status(
                booking=booking, new_status=data["status"], actor=request.user,
                reason=data.get("reason", ""),
            )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking updated successfully.")

    @extend_schema(
        summary="Cancel a booking",
        responses={
            200: inline_serializer(
                name="BookingDeleteResponse",
                fields={
                    "success": serializers.BooleanField(default=True),
                    "message": serializers.CharField(default="Booking cancelled successfully"),
                },
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        services.cancel_booking(booking=booking, actor=request.user,
                                reason="Cancelled by admin")
        return Response(
            {"success": True, "message": "Booking cancelled successfully"},
            status=http_status.HTTP_200_OK,
        )

    @extend_schema(summary="Reschedule any booking")
    @action(detail=True, methods=["patch"])
    def reschedule(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = services.reschedule_booking(
            booking=booking, new_slot_id=serializer.validated_data["new_slot_id"],
            actor=request.user,
        )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking rescheduled successfully.")

    @extend_schema(summary="Mark a booking as completed")
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        booking = services.mark_completed(booking=self.get_object(), actor=request.user)
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking marked as completed.")

    @extend_schema(summary="Cancel a booking")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = services.cancel_booking(
            booking=self.get_object(), actor=request.user,
            reason=request.data.get("reason", "Cancelled by admin"),
        )
        return success_response(data=BookingSerializer(booking).data,
                                message="Booking cancelled successfully.")

    @extend_schema(tags=["admin-reminders"],
                   summary="Manually send a booking reminder email")
    @action(detail=True, methods=["post"], url_path="send-reminder")
    def send_reminder(self, request, pk=None):
        from notifications.services import send_manual_reminder
        from notifications.serializers import ReminderSerializer

        booking = get_object_or_404(Booking, pk=pk)
        reminder = send_manual_reminder(booking=booking, actor=request.user)
        return success_response(data=ReminderSerializer(reminder).data,
                                message="Reminder sent successfully.")

    @extend_schema(
        tags=["admin-reminders"],
        summary="List reminders for one booking",
        description="Returns automatic and manually sent reminder records for this booking, newest first.",
        responses=ReminderSerializer(many=True),
    )
    @action(detail=True, methods=["get"], url_path="reminders")
    def reminders(self, request, pk=None):
        """Return the reminder history for the selected booking."""
        from notifications.models import Reminder

        booking = self.get_object()
        queryset = Reminder.objects.filter(booking=booking).order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(ReminderSerializer(page, many=True).data)
        return Response(ReminderSerializer(queryset, many=True).data)

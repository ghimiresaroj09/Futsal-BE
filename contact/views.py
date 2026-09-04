"""Contact APIs."""
from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.responses import success_response
from contact.models import ContactMessage
from contact.serializers import AdminContactUpdateSerializer, ContactMessageSerializer


@extend_schema(tags=["contact"], summary="Submit a contact message", auth=[])
class ContactCreateViewSet(EnvelopeMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    throttle_scope = "contact"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return success_response(data=ContactMessageSerializer(message).data,
                                message="Your message has been submitted successfully.",
                                status=status.HTTP_201_CREATED)


@extend_schema(tags=["admin-contact"], summary="Admin contact message management")
class AdminContactViewSet(EnvelopeMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ContactMessage.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_fields = ["status", "email"]
    search_fields = ["name", "email", "subject", "phone_number"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return AdminContactUpdateSerializer
        return ContactMessageSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return success_response(data=ContactMessageSerializer(message).data,
                                message="Contact message updated successfully.")

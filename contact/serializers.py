from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from common.validators import validate_full_name, validate_phone_number
from contact.models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "phone_number", "subject", "message",
                  "status", "admin_notes", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "admin_notes", "created_at", "updated_at"]

    def validate_name(self, value):
        try:
            return validate_full_name(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_phone_number(self, value):
        try:
            return validate_phone_number(value.strip())
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))


class AdminContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["status", "admin_notes"]

"""Accounts serializers: validation only, no business logic."""
from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import User
from common.enums import OTPPurpose
from common.validators import validate_full_name, validate_image_upload, validate_phone_number


def _password_field(**kwargs) -> serializers.CharField:
    return serializers.CharField(write_only=True, style={"input_type": "password"}, **kwargs)


def _run_password_validators(password: str, user=None) -> None:
    try:
        validate_password(password, user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "phone_number", "profile_image", "role",
                  "is_verified", "created_at"]
        read_only_fields = ["id", "role", "is_verified", "created_at"]

    def get_profile_image(self, obj) -> str | None:
        if not obj.profile_image:
            return None
        url = obj.profile_image.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request and url.startswith("/") else url


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    password = _password_field()
    confirm_password = _password_field()

    def validate_full_name(self, value: str) -> str:
        try:
            return validate_full_name(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        try:
            validate_phone_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})
        try:
            _run_password_validators(attrs["password"])
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({"password": exc.detail})
        return attrs


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(r"^\d{6}$")
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.choices, default=OTPPurpose.REGISTRATION
    )


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.choices, default=OTPPurpose.REGISTRATION
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = _password_field()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = _password_field()
    new_password = _password_field()
    confirm_password = _password_field()

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": ["Old password is incorrect."]})
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": ["New password cannot be the same as the old password."]}
            )
        try:
            _run_password_validators(attrs["new_password"], user)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({"new_password": exc.detail})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.RegexField(r"^\d{6}$")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField()
    new_password = _password_field()
    confirm_password = _password_field()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": ["Passwords do not match."]})
        try:
            _run_password_validators(attrs["new_password"])
        except serializers.ValidationError as exc:
            raise serializers.ValidationError({"new_password": exc.detail})
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number", "profile_image"]

    def validate_full_name(self, value: str) -> str:
        try:
            return validate_full_name(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        try:
            validate_phone_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        if User.objects.filter(phone_number=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate_profile_image(self, value):
        try:
            return validate_image_upload(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))

    def update(self, instance, validated_data):
        new_email = validated_data.get("email")
        if new_email and new_email != instance.email:
            # Email change requires re-verification.
            instance.is_verified = False
        return super().update(instance, validated_data)

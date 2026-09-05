"""Authentication, profile and admin-profile API views."""
from __future__ import annotations

import logging

from django.db.models import Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts import services
from accounts.models import User
from accounts.selectors import get_user_by_email
from accounts.serializers import (
    ChangePasswordSerializer, ForgotPasswordSerializer, LoginSerializer, LogoutSerializer,
    ProfileUpdateSerializer, RefreshSerializer, RegisterSerializer, ResendOTPSerializer,
    ResetPasswordSerializer, UserSerializer, VerifyForgotPasswordOTPSerializer,
    VerifyOTPSerializer,
)
from accounts.tokens import make_reset_token, read_reset_token
from bookings.filters import BookingFilter
from bookings.selectors import bookings_queryset
from bookings.serializers import BookingSerializer
from common.enums import OTPPurpose
from common.exceptions import ServiceError
from common.permissions import IsAdmin
from common.responses import success_response
from common.mixins import EnvelopeMixin

logger = logging.getLogger("futsal.auth")


class BaseAuthView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def validated(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


@extend_schema(tags=["auth"], summary="Register a new (unverified) user and send a registration OTP")
class RegisterView(BaseAuthView):
    serializer_class = RegisterSerializer
    throttle_scope = "register"

    def post(self, request):
        data = self.validated(request)
        user = services.register_user(
            full_name=data["full_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            password=data["password"],
        )
        return success_response(
            data=UserSerializer(user).data,
            message="Registration successful. An OTP has been sent to your email.",
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["auth"], summary="Verify an OTP for a given purpose")
class VerifyOTPView(BaseAuthView):
    serializer_class = VerifyOTPSerializer
    throttle_scope = "otp"

    def post(self, request):
        data = self.validated(request)
        user = get_user_by_email(data["email"])
        if user is None:
            raise ServiceError("Invalid OTP.", errors={"otp": ["Invalid OTP."]})
        purpose = data["purpose"]
        services.verify_otp(user=user, code=data["otp"], purpose=purpose)
        if purpose == OTPPurpose.REGISTRATION:
            services.activate_user(user)
            tokens = services.issue_tokens(user)
            return success_response(
                data={**tokens, "user": UserSerializer(user).data},
                message="Account verified successfully.",
            )
        return success_response(
            data={"reset_token": make_reset_token(user.id)},
            message="OTP verified successfully.",
        )


@extend_schema(tags=["auth"], summary="Resend an OTP (rate limited)")
class ResendOTPView(BaseAuthView):
    serializer_class = ResendOTPSerializer
    throttle_scope = "otp"

    def post(self, request):
        data = self.validated(request)
        user = get_user_by_email(data["email"])
        if user is not None:
            if data["purpose"] == OTPPurpose.REGISTRATION and user.is_verified:
                raise ServiceError("Account is already verified.",
                                   errors={"email": ["Account is already verified."]})
            services.issue_otp(user=user, purpose=data["purpose"])
        return success_response(message="If the account exists, an OTP has been sent.")


@extend_schema(tags=["auth"], summary="Login and obtain JWT access/refresh tokens")
class LoginView(BaseAuthView):
    serializer_class = LoginSerializer
    throttle_scope = "login"

    def post(self, request):
        data = self.validated(request)
        user, tokens = services.login_user(email=data["email"], password=data["password"])
        return success_response(
            data={**tokens, "user": UserSerializer(user).data}, message="Login successful."
        )


@extend_schema(
    tags=["auth"],
    summary="Rotate refresh token: returns a NEW access and a NEW refresh token",
    responses={200: OpenApiResponse(description="New access and refresh tokens")},
)
class RefreshView(BaseAuthView):
    serializer_class = RefreshSerializer

    def post(self, request):
        data = self.validated(request)
        try:
            old = RefreshToken(data["refresh"])
            user_id = old["user_id"]
            old.blacklist()  # rotation: previous refresh token is invalidated
        except TokenError:
            raise ServiceError("Invalid or expired refresh token.",
                               errors={"refresh": ["Invalid or expired refresh token."]})
        from accounts.models import User

        user = User.objects.filter(id=user_id, is_active=True).first()
        if user is None:
            raise ServiceError("Invalid refresh token.",
                               errors={"refresh": ["Invalid refresh token."]})
        return success_response(data=services.issue_tokens(user), message="Token refreshed.")


@extend_schema(tags=["auth"], summary="Logout and blacklist the refresh token")
class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            raise ServiceError("Invalid or expired refresh token.",
                               errors={"refresh": ["Invalid or expired refresh token."]})
        logger.info("User logged out id=%s", request.user.id)
        return success_response(message="Logout successful.", status=status.HTTP_200_OK)


@extend_schema(tags=["auth"], summary="Change password (invalidates existing refresh tokens)")
class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return success_response(message="Password changed successfully. Please login again.")


@extend_schema(tags=["auth"], summary="Request a forgot-password OTP")
class ForgotPasswordView(BaseAuthView):
    serializer_class = ForgotPasswordSerializer
    throttle_scope = "otp"

    def post(self, request):
        data = self.validated(request)
        user = get_user_by_email(data["email"])
        if user is None or not user.is_active:
            raise ServiceError(
                "No active account exists with that email.",
                errors={"email": ["No active account exists with that email."]},
            )
        services.issue_otp(user=user, purpose=OTPPurpose.FORGOT_PASSWORD)
        return success_response(
            message="A password reset OTP has been sent to your email."
        )


@extend_schema(tags=["auth"], summary="Verify forgot-password OTP and receive a reset token")
class VerifyForgotPasswordOTPView(BaseAuthView):
    serializer_class = VerifyForgotPasswordOTPSerializer
    throttle_scope = "otp"

    def post(self, request):
        data = self.validated(request)
        user = get_user_by_email(data["email"])
        if user is None:
            raise ServiceError("Invalid OTP.", errors={"otp": ["Invalid OTP."]})
        services.verify_otp(user=user, code=data["otp"], purpose=OTPPurpose.FORGOT_PASSWORD)
        return success_response(
            data={"reset_token": make_reset_token(user.id)}, message="OTP verified successfully."
        )


@extend_schema(tags=["auth"], summary="Set a new password using the reset token")
class ResetPasswordView(BaseAuthView):
    serializer_class = ResetPasswordSerializer
    throttle_scope = "otp"

    def post(self, request):
        data = self.validated(request)
        user_id = read_reset_token(data["reset_token"])
        user = get_user_by_email(data["email"])
        if user is None or user_id is None or str(user.id) != user_id:
            raise ServiceError("Invalid or expired reset token.",
                               errors={"reset_token": ["Invalid or expired reset token."]})
        services.reset_password(user=user, new_password=data["new_password"])
        return success_response(message="Password reset successfully. Please login.")


@extend_schema(tags=["users"], summary="Retrieve or update the authenticated user's profile")
class MeView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return success_response(data=UserSerializer(request.user, context={"request": request}).data,
                                message="Profile retrieved successfully.")

    @extend_schema(request=ProfileUpdateSerializer, responses={200: UserSerializer})
    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(data=UserSerializer(user, context={"request": request}).data,
                                message="Profile updated successfully.")


@extend_schema(tags=["admin-profile"], summary="Admin profile (view and update)")
class AdminProfileView(MeView):
    permission_classes = [IsAuthenticated, IsAdmin]


@extend_schema(tags=["admin-users"], summary="List all non-admin users")
class AdminUserViewSet(EnvelopeMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.filter(role="USER")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    search_fields = ["full_name", "email", "phone_number"]
    ordering_fields = ["created_at", "full_name", "email"]
    ordering = ["-created_at"]

    @extend_schema(
        summary="List a non-admin user's booking history",
        description=(
            "Returns bookings owned by the selected non-admin user, including bookings "
            "an admin created on their behalf using the user's email address. Supports "
            "the same filters, search, ordering, and pagination as the admin booking list."
        ),
        responses=BookingSerializer(many=True),
    )
    @action(detail=True, methods=["get"], url_path="booking-history")
    def booking_history(self, request, pk=None):
        """Return the selected customer's complete booking history."""
        user = self.get_object()
        queryset = self.filter_queryset(
            bookings_queryset().filter(
                Q(user=user) | Q(booking_source="ADMIN", email__iexact=user.email)
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                BookingSerializer(page, many=True, context={"request": request}).data
            )
        return Response(BookingSerializer(queryset, many=True, context={"request": request}).data)


@extend_schema(tags=["admin-profile"], summary="Admin change password")
class AdminChangePasswordView(ChangePasswordView):
    permission_classes = [IsAuthenticated, IsAdmin]

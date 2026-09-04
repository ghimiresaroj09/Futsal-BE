"""Admin dashboard and revenue APIs."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from common.permissions import IsAdmin
from common.responses import success_response
from common.utils import parse_date
from dashboard.selectors import analytics, bookings_series, slot_analytics, today_overview
from payments.selectors import revenue_series, revenue_summary

PERIOD_PARAM = OpenApiParameter(
    "period", str, description="Grouping period: day | week | month (default: day)"
)
DATE_PARAMS = [
    OpenApiParameter("start_date", str, description="Start date YYYY-MM-DD"),
    OpenApiParameter("end_date", str, description="End date YYYY-MM-DD"),
]


class EmptySerializer(serializers.Serializer):
    """Placeholder for read-only analytics endpoints (no request body)."""


class AdminBaseView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = EmptySerializer

    def range(self, request):
        return (parse_date(request.query_params.get("start_date")),
                parse_date(request.query_params.get("end_date")))

    def period(self, request) -> str:
        period = (request.query_params.get("period") or "day").lower()
        return period if period in {"day", "week", "month"} else "day"


@extend_schema(tags=["analytics"], responses={200: dict}, summary="Analytics dashboard", parameters=[
    OpenApiParameter("start_date", str, description="Start date YYYY-MM-DD"),
    OpenApiParameter("end_date", str, description="End date YYYY-MM-DD"),
    OpenApiParameter("period", str, description="7d | 30d | 6m | 12m (default: 6m)"),
    OpenApiParameter("futsal", str, description="Optional futsal UUID"),
    OpenApiParameter("timezone", str, description="Reporting timezone (metadata)"),
])
class AnalyticsView(AdminBaseView):
    def get(self, request):
        import datetime as dt
        from django.utils import timezone
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        start, end = self.range(request)
        for name, value in (("start_date", start), ("end_date", end)):
            if request.query_params.get(name) and value is None:
                raise ValidationError({name: ["Use YYYY-MM-DD format."]})
        period = (request.query_params.get("period") or "6m").lower()
        if period not in {"7d", "30d", "6m", "12m"}:
            raise ValidationError({"period": ["Use 7d, 30d, 6m, or 12m."]})
        timezone_name = request.query_params.get("timezone") or timezone.get_current_timezone_name()
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            raise ValidationError({"timezone": ["Use a valid IANA timezone."]})
        end = end or timezone.localdate()
        start = start or (end - dt.timedelta(days={"7d": 6, "30d": 29, "6m": 182, "12m": 364}[period]))
        if start > end:
            raise ValidationError({"start_date": ["Start date must be before end date."]})
        futsal_id = request.query_params.get("futsal")
        if futsal_id:
            from uuid import UUID
            try:
                UUID(futsal_id)
            except ValueError:
                raise ValidationError({"futsal": ["Use a valid UUID."]})
        data = analytics(start, end, period=period, futsal_id=futsal_id)
        data["period"] = {"start_date": start, "end_date": end, "timezone": timezone_name}
        return success_response(data=data, message="Analytics retrieved successfully.")


@extend_schema(tags=["admin-dashboard"], responses={200: dict}, summary="Admin dashboard: today's overview and slot analytics")
class DashboardView(AdminBaseView):
    def get(self, request):
        start, end = self.range(request)
        return success_response(
            data={
                "today": today_overview(),
                "slots": slot_analytics(start, end),
                "revenue_summary": revenue_summary(start, end),
            },
            message="Dashboard data retrieved successfully.",
        )


@extend_schema(tags=["admin-dashboard"], responses={200: dict}, summary="Graph-ready revenue series", parameters=[PERIOD_PARAM, *DATE_PARAMS])
class DashboardRevenueView(AdminBaseView):
    def get(self, request):
        start, end = self.range(request)
        return success_response(
            data=revenue_series(self.period(request), start, end),
            message="Revenue graph data retrieved successfully.",
        )


@extend_schema(tags=["admin-dashboard"], responses={200: dict}, summary="Graph-ready booking series", parameters=[PERIOD_PARAM, *DATE_PARAMS])
class DashboardBookingsView(AdminBaseView):
    def get(self, request):
        start, end = self.range(request)
        return success_response(
            data=bookings_series(self.period(request), start, end),
            message="Booking graph data retrieved successfully.",
        )


@extend_schema(tags=["admin-dashboard"], responses={200: dict}, summary="Slot analytics and occupancy rate", parameters=DATE_PARAMS)
class DashboardSlotsView(AdminBaseView):
    def get(self, request):
        start, end = self.range(request)
        return success_response(data=slot_analytics(start, end),
                                message="Slot analytics retrieved successfully.")

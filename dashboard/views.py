"""Admin dashboard and revenue APIs."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.views import APIView

from common.permissions import IsAdmin
from common.responses import success_response
from common.utils import parse_date
from dashboard.selectors import bookings_series, slot_analytics, today_overview
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


@extend_schema(tags=["admin-revenue"], responses={200: dict}, summary="Revenue summary", parameters=[
    *DATE_PARAMS,
    OpenApiParameter("payment_status", str, description="PENDING | PAID | FAILED | REFUNDED"),
])
class RevenueView(AdminBaseView):
    def get(self, request):
        start, end = self.range(request)
        data = revenue_summary(start, end, request.query_params.get("payment_status"))
        return success_response(data=data, message="Revenue retrieved successfully.")


class _PeriodRevenueView(AdminBaseView):
    period_name = "day"

    def get(self, request):
        start, end = self.range(request)
        return success_response(
            data={
                "summary": revenue_summary(start, end),
                "series": revenue_series(self.period_name, start, end),
            },
            message="Revenue retrieved successfully.",
        )


@extend_schema(tags=["admin-revenue"], responses={200: dict}, summary="Daily revenue", parameters=DATE_PARAMS)
class DailyRevenueView(_PeriodRevenueView):
    period_name = "day"


@extend_schema(tags=["admin-revenue"], responses={200: dict}, summary="Weekly revenue", parameters=DATE_PARAMS)
class WeeklyRevenueView(_PeriodRevenueView):
    period_name = "week"


@extend_schema(tags=["admin-revenue"], responses={200: dict}, summary="Monthly revenue", parameters=DATE_PARAMS)
class MonthlyRevenueView(_PeriodRevenueView):
    period_name = "month"

"""Analytics and operational dashboard APIs."""
from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from common.permissions import IsAdmin
from common.responses import success_response
from common.utils import parse_date
from dashboard.selectors import analytics, operational_dashboard
from futsal.models import Futsal

class EmptySerializer(serializers.Serializer):
    """Placeholder for read-only analytics endpoints (no request body)."""


class AdminBaseView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = EmptySerializer

    def range(self, request):
        return (parse_date(request.query_params.get("start_date")),
                parse_date(request.query_params.get("end_date")))

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


@extend_schema(tags=["dashboard"], responses={200: dict}, summary="Today's operational dashboard", parameters=[
    OpenApiParameter("date", str, description="Operating date YYYY-MM-DD"),
    OpenApiParameter("futsal", str, description="Optional futsal UUID"),
    OpenApiParameter("timezone", str, description="Timezone for date and time calculations"),
])
class DashboardView(AdminBaseView):
    def get(self, request):
        from django.utils import timezone
        from rest_framework.exceptions import NotFound
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        requested_date = request.query_params.get("date")
        date = parse_date(requested_date)
        if requested_date and date is None:
            raise ValidationError({"date": ["Use YYYY-MM-DD format."]})
        timezone_name = request.query_params.get("timezone") or timezone.get_current_timezone_name()
        try:
            zone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            raise ValidationError({"timezone": ["Use a valid IANA timezone."]})
        futsal_id = request.query_params.get("futsal")
        if futsal_id:
            from uuid import UUID
            try:
                UUID(futsal_id)
            except ValueError:
                raise ValidationError({"futsal": ["Use a valid UUID."]})
        futsal = Futsal.objects.filter(pk=futsal_id).first() if futsal_id else Futsal.objects.get_solo()
        if futsal is None:
            raise NotFound("Facility not found.")
        now = timezone.localtime(timezone.now(), zone)
        data = operational_dashboard(date or now.date(), futsal=futsal, now=now)
        data["timezone"] = timezone_name
        return success_response(data=data, message="Dashboard retrieved successfully.")

"""Booking filters for user and admin lists."""
from __future__ import annotations

import django_filters as filters

from bookings.models import Booking


class BookingFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="slot__date")
    start_date = filters.DateFilter(field_name="slot__date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="slot__date", lookup_expr="lte")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    source = filters.CharFilter(field_name="booking_source", lookup_expr="iexact")
    email = filters.CharFilter(field_name="email", lookup_expr="iexact")
    phone = filters.CharFilter(field_name="phone_number", lookup_expr="icontains")
    booking_reference = filters.CharFilter(field_name="booking_reference",
                                           lookup_expr="iexact")
    futsal = filters.UUIDFilter(field_name="futsal_id")

    class Meta:
        model = Booking
        fields = ["date", "start_date", "end_date", "status", "source", "email",
                  "phone", "booking_reference", "futsal"]

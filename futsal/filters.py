"""Slot filters."""
from __future__ import annotations

import django_filters as filters

from futsal.models import Slot


class SlotFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="date")
    start_date = filters.DateFilter(field_name="date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="date", lookup_expr="lte")
    status = filters.CharFilter(field_name="status", lookup_expr="iexact")
    futsal = filters.UUIDFilter(field_name="futsal_id")

    class Meta:
        model = Slot
        fields = ["date", "status", "futsal", "start_date", "end_date"]

"""Slot query helpers."""
from __future__ import annotations

from futsal.models import Slot


def slots_queryset():
    return Slot.objects.select_related("futsal")

from django.contrib import admin

from futsal.models import Futsal, FutsalClosure, FutsalMedia, Slot


@admin.register(Futsal)
class FutsalAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "price_per_slot", "status"]
    search_fields = ["name", "location"]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ["date", "start_time", "end_time", "futsal", "status"]
    list_filter = ["status", "date"]


@admin.register(FutsalClosure)
class FutsalClosureAdmin(admin.ModelAdmin):
    list_display = ["date", "reason", "created_at"]
    list_filter = ["date"]


@admin.register(FutsalMedia)
class FutsalMediaAdmin(admin.ModelAdmin):
    list_display = ["media_type", "futsal", "caption", "is_cover", "sort_order", "created_at"]
    list_filter = ["media_type", "is_cover"]
    ordering = ["sort_order", "-created_at"]

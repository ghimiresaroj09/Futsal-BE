from django.contrib import admin

from futsal.models import Futsal, FutsalClosure, FutsalMedia, Slot


@admin.register(Futsal)
class FutsalAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "price_per_slot", "status"]
    search_fields = ["name", "location"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "location", "address", "phone", "email", "status")
        }),
        ("Pricing & Schedule", {
            "fields": ("price_per_slot", "slot_duration", "opening_time", "closing_time")
        }),
        ("Social Media", {
            "fields": ("facebook", "instagram", "twitter", "tiktok"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]


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

from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["booking_reference", "full_name", "slot", "status",
                    "booking_source", "amount"]
    list_filter = ["status", "booking_source"]
    search_fields = ["booking_reference", "full_name", "email", "phone_number"]

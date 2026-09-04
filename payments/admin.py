from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["booking", "amount", "payment_status", "payment_method", "paid_at"]
    list_filter = ["payment_status", "payment_method"]

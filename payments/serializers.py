from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "amount", "advance_amount", "remaining_amount",
                  "refunded_amount", "payment_status",
                  "payment_method", "transaction_reference", "paid_at",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "booking", "created_at", "updated_at"]


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["payment_status", "payment_method", "transaction_reference", "amount",
                  "advance_amount"]

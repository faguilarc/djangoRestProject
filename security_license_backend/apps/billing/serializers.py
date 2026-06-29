from rest_framework import serializers
from .models import PaymentMethod, Invoice, InvoiceItem, Subscription, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'company', 'invoice_number', 'date_issued', 'due_date', 'total_amount', 'status', 'items']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'company', 'plan', 'start_date', 'end_date', 'status', 'auto_renew']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'amount', 'currency', 'payment_method_type', 'transaction_id', 'status', 'paid_at']
        read_only_fields = ['paid_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod;
        fields = '__all__'

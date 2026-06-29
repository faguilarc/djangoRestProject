from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PaymentMethod, Invoice, InvoiceItem, Subscription, Payment


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer para PaymentMethod"""
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'user', 'user_email', 'provider', 'provider_method_id',
            'card_last_four', 'card_brand', 'expiry_month', 'expiry_year',
            'is_default', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'provider_method_id': {'write_only': True}
        }


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer para InvoiceItem"""
    description = serializers.CharField(source='invoice.description', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'description', 'quantity', 'unit_price',
            'total_amount', 'metadata', 'created_at'
        ]
        read_only_fields = ['total_amount', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer para Invoice"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'company', 'company_name', 'subscription', 'invoice_number',
            'status', 'issue_date', 'due_date', 'paid_date', 'subtotal',
            'tax_amount', 'discount_amount', 'total_amount', 'items',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'invoice_number', 'total_amount', 'paid_date', 
            'created_at', 'updated_at'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para Subscription"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'company', 'company_name', 'plan', 'plan_name',
            'status', 'start_date', 'end_date', 'current_period_start',
            'current_period_end', 'cancel_at_period_end', 'canceled_at',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para Payment"""
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_method_type = serializers.CharField(source='payment_method.provider', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'payment_method', 
            'payment_method_type', 'amount', 'currency', 'status',
            'transaction_id', 'processed_at', 'failure_reason',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['processed_at', 'created_at', 'updated_at']

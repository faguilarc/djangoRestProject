from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Plan, License, LicenseActivation, LicenseUsage


class PlanSerializer(serializers.ModelSerializer):
    """Serializer para Plan"""
    
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'description', 'code', 'max_users', 
            'max_activations', 'duration_days', 'price', 'currency',
            'is_active', 'features', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LicenseSerializer(serializers.ModelSerializer):
    """Serializer para License"""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = License
        fields = [
            'id', 'license_key', 'plan', 'plan_name', 'company', 'company_name',
            'status', 'issued_at', 'expires_at', 'activated_at', 'deactivated_at',
            'max_users', 'max_activations', 'activation_count', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'license_key', 'activated_at', 'deactivated_at', 
            'activation_count', 'created_at', 'updated_at'
        ]


class LicenseActivationSerializer(serializers.ModelSerializer):
    """Serializer para LicenseActivation"""
    license_key_str = serializers.CharField(source='license.license_key', read_only=True)

    class Meta:
        model = LicenseActivation
        fields = [
            'id', 'license', 'license_key_str', 'machine_id', 'machine_name',
            'ip_address', 'activated_at', 'deactivated_at', 'is_active',
            'last_heartbeat', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['activated_at', 'deactivated_at', 'created_at', 'updated_at']


class LicenseUsageSerializer(serializers.ModelSerializer):
    """Serializer para LicenseUsage"""
    license_key_str = serializers.CharField(source='license.license_key', read_only=True)

    class Meta:
        model = LicenseUsage
        fields = [
            'id', 'license', 'license_key_str', 'metric_name', 'metric_value',
            'recorded_at', 'metadata', 'created_at'
        ]
        read_only_fields = ['recorded_at', 'created_at']

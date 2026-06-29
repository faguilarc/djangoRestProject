from rest_framework import serializers
from .models import Plan, License, LicenseActivation, LicenseUsage


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'code', 'max_users', 'max_activations', 'duration_days', 'price', 'features_json',
                  'is_active']


class LicenseSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = License
        fields = ['id', 'license_key', 'plan', 'plan_name', 'company', 'company_name',
                  'issued_at', 'expires_at', 'status', 'metadata_json']
        read_only_fields = ['license_key', 'issued_at', 'expires_at', 'status']


class LicenseActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseActivation
        fields = ['id', 'license', 'machine_id', 'activated_at', 'last_seen', 'is_active']
        read_only_fields = ['activated_at', 'last_seen']


class LicenseUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseUsage
        fields = ['id', 'license', 'metric_name', 'value', 'recorded_at']
        read_only_fields = ['recorded_at']
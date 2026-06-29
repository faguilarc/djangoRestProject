from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Company, Contact, Interaction


class CompanySerializer(serializers.ModelSerializer):
    """Serializer para Company"""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'tax_id', 'email', 'phone', 'address', 
            'city', 'state', 'country', 'postal_code', 'website',
            'industry', 'status', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    """Serializer para Contact"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'company', 'company_name', 'user', 'user_email',
            'first_name', 'last_name', 'email', 'phone', 'position',
            'department', 'is_primary', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InteractionSerializer(serializers.ModelSerializer):
    """Serializer para Interaction"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    contact_name = serializers.CharField(source='contact.get_full_name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = Interaction
        fields = [
            'id', 'company', 'company_name', 'contact', 'contact_name',
            'interaction_type', 'subject', 'description', 'status',
            'scheduled_at', 'completed_at', 'created_by', 'created_by_email',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

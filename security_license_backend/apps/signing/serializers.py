from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import SigningKey, Signature, Document
from apps.crm.serializers import CompanySerializer
from apps.iam.serializers import UserSerializer


class SigningKeySerializer(serializers.ModelSerializer):
    """Serializer para SigningKey"""
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = SigningKey
        fields = [
            'id', 'owner', 'owner_name', 'user', 'user_email', 'name', 
            'algorithm', 'purpose', 'public_key', 'fingerprint', 
            'is_active', 'expires_at', 'created_by', 'created_by_email', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['public_key', 'fingerprint', 'created_at', 'updated_at']
        extra_kwargs = {
            'private_key_encrypted': {'write_only': True}
        }


class SignatureSerializer(serializers.ModelSerializer):
    """Serializer para Signature"""
    signing_key_name = serializers.CharField(source='signing_key.name', read_only=True)
    signer_email = serializers.EmailField(source='signer.email', read_only=True)

    class Meta:
        model = Signature
        fields = [
            'id', 'signing_key', 'signing_key_name', 'signer', 'signer_email',
            'type', 'status', 'original_hash', 'signature_value', 'metadata',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['signature_value', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer para Document"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'company', 'company_name', 'user', 'user_email',
            'title', 'description', 'file_path', 'file_hash', 'file_size',
            'mime_type', 'status', 'requires_signature', 'signed_at',
            'verified_at', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['file_hash', 'file_size', 'mime_type', 'created_at', 'updated_at', 'signed_at', 'verified_at']

    def validate_file_path(self, value):
        if not value:
            raise serializers.ValidationError(_("file_path is required."))
        return value

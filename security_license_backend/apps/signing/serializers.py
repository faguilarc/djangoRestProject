from rest_framework import serializers
from .models import SigningKey, Signature, Document


class SigningKeySerializer(serializers.ModelSerializer):
    # Nunca exponemos private_key_encrypted ni public_key_raw en lectura normal si es sensible
    class Meta:
        model = SigningKey
        fields = ['id', 'user', 'name', 'algorithm', 'created_at', 'is_active']
        read_only_fields = ['created_at', 'public_key_raw']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'title', 'file', 'hash_original', 'created_at']
        read_only_fields = ['hash_original', 'created_at']


class SignatureSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    signer_email = serializers.EmailField(source='signing_key.user.email', read_only=True)

    class Meta:
        model = Signature
        fields = ['id', 'document', 'document_title', 'signing_key', 'signer_email',
                  'signature_data', 'signed_at', 'verification_status']
        read_only_fields = ['signed_at', 'verification_status']
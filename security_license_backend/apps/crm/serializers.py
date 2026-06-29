from rest_framework import serializers
from .models import Company, Contact, Interaction

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = ['id', 'name', 'tax_id', 'address', 'phone', 'website', 'contacts', 'created_at']

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'
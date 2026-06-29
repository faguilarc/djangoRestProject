from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, UserRoles, Menu, AuditLog

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions_json', 'created_at']

class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'url', 'icon', 'order', 'parent', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return MenuSerializer(obj.children.all(), many=True).data
        return None

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'resource_type', 'resource_id', 'details', 'timestamp']
        read_only_fields = ['user', 'timestamp']
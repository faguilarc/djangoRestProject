from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model
from .models import User, Role, Menu, AuditLog, UserRoles
from .serializers import UserSerializer, RoleSerializer, MenuSerializer, AuditLogSerializer

UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    """
    queryset = User.objects.select_related('profile').all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.select_related('profile').all().order_by('-date_joined')
        return User.objects.filter(id=user.id).select_related('profile')

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener datos del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar roles.
    """
    queryset = Role.objects.prefetch_related('permissions', 'menus').all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet solo lectura para consultar menús disponibles.
    """
    queryset = Menu.objects.filter(is_active=True).order_by('parent', 'order')
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_menu(self, request):
        """
        Obtiene el menú filtrado por los permisos del usuario autenticado.
        """
        user = request.user
        if user.is_superuser:
            menus = Menu.objects.filter(is_active=True).order_by('parent', 'order')
        else:
            # Obtener roles del usuario
            user_roles = UserRoles.objects.filter(user=user).values_list('role_id', flat=True)
            menus = Menu.objects.filter(
                is_active=True,
                roles__in=user_roles
            ).distinct().order_by('parent', 'order')
        
        serializer = self.get_serializer(menus, many=True)
        return Response(serializer.data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet solo lectura para consultar logs de auditoría.
    """
    queryset = AuditLog.objects.select_related('user').all().order_by('-created_at')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo admins pueden ver logs

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.select_related('user').all().order_by('-created_at')
        # Admins normales solo ven logs relacionados con su empresa/rol
        return AuditLog.objects.filter(user=user).order_by('-created_at')

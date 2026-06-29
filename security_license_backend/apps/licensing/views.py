from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from .models import Plan, License, LicenseActivation, LicenseUsage
from .serializers import PlanSerializer, LicenseSerializer, LicenseActivationSerializer, LicenseUsageSerializer


class PlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar planes de licenciamiento.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Plan.objects.all()
        return Plan.objects.filter(is_active=True)


class LicenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar licencias.
    """
    queryset = License.objects.select_related('plan', 'company').all().order_by('-created_at')
    serializer_class = LicenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return License.objects.select_related('plan', 'company').all().order_by('-created_at')
        return License.objects.filter(
            models.Q(company__contacts__user=user)
        ).distinct().select_related('plan', 'company').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        license_obj = self.get_object()
        if license_obj.status != 'ACTIVE':
            return Response({'error': 'License is not active'}, status=status.HTTP_400_BAD_REQUEST)
        
        license_obj.activated_at = timezone.now()
        license_obj.save(update_fields=['activated_at'])
        return Response({'status': 'license activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        license_obj = self.get_object()
        license_obj.status = 'DEACTIVATED'
        license_obj.deactivated_at = timezone.now()
        license_obj.save(update_fields=['status', 'deactivated_at'])
        return Response({'status': 'license deactivated'})


class LicenseActivationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar activaciones de licencias por máquina.
    """
    queryset = LicenseActivation.objects.select_related('license').all().order_by('-created_at')
    serializer_class = LicenseActivationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return LicenseActivation.objects.select_related('license').all().order_by('-created_at')
        return LicenseActivation.objects.filter(
            models.Q(license__company__contacts__user=user)
        ).distinct().select_related('license').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        activation = self.get_object()
        activation.last_heartbeat = timezone.now()
        activation.save(update_fields=['last_heartbeat'])
        return Response({'status': 'heartbeat recorded', 'timestamp': activation.last_heartbeat})


class LicenseUsageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registrar y consultar métricas de uso de licencias.
    """
    queryset = LicenseUsage.objects.select_related('license').all().order_by('-recorded_at')
    serializer_class = LicenseUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return LicenseUsage.objects.select_related('license').all().order_by('-recorded_at')
        return LicenseUsage.objects.filter(
            models.Q(license__company__contacts__user=user)
        ).distinct().select_related('license').order_by('-recorded_at')

    def perform_create(self, serializer):
        serializer.save(recorded_at=timezone.now())

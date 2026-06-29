from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from .models import Plan, License, LicenseActivation, LicenseUsage
from .serializers import PlanSerializer, LicenseSerializer, LicenseActivationSerializer, LicenseUsageSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        license_obj = self.get_object()
        machine_id = request.data.get('machine_id')
        # Aquí iría la lógica real de activación
        activation, created = LicenseActivation.objects.get_or_create(
            license=license_obj,
            machine_id=machine_id,
            defaults={'is_active': True}
        )
        return Response({'status': 'activated', 'activation_id': activation.id})

    @decorators.action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        license_obj = self.get_object()
        is_valid = license_obj.is_valid()
        return Response({'valid': is_valid, 'status': license_obj.status})

class LicenseActivationViewSet(viewsets.ModelViewSet):
    queryset = LicenseActivation.objects.all()
    serializer_class = LicenseActivationSerializer
    permission_classes = [permissions.IsAuthenticated]

class LicenseUsageViewSet(viewsets.ModelViewSet):
    queryset = LicenseUsage.objects.all()
    serializer_class = LicenseUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
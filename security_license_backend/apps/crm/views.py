from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Company, Contact, Interaction
from .serializers import CompanySerializer, ContactSerializer, InteractionSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empresas/clientes.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        # Usuarios normales ven las empresas donde son contactos
        return Company.objects.filter(contacts__user=user).distinct()


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar contactos de empresas.
    """
    queryset = Contact.objects.select_related('company', 'user').all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Contact.objects.select_related('company', 'user').all()
        # Usuarios ven sus propios contactos o los de su empresa
        return Contact.objects.filter(
            models.Q(user=user) |
            models.Q(company__contacts__user=user)
        ).distinct().select_related('company', 'user')

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario si no se proporciona
        if not serializer.validated_data.get('user'):
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class InteractionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar interacciones con clientes.
    """
    queryset = Interaction.objects.select_related('company', 'contact', 'created_by').all().order_by('-created_at')
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Interaction.objects.select_related('company', 'contact', 'created_by').all().order_by('-created_at')
        # Usuarios ven interacciones de sus empresas o creadas por ellos
        return Interaction.objects.filter(
            models.Q(company__contacts__user=user) |
            models.Q(created_by=user)
        ).distinct().select_related('company', 'contact', 'created_by').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

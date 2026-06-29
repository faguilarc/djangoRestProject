from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from .models import SigningKey, Signature, Document
from .serializers import SigningKeySerializer, SignatureSerializer, DocumentSerializer


class SigningKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar claves de firma digital.
    """
    queryset = SigningKey.objects.select_related('owner', 'user', 'created_by').all()
    serializer_class = SigningKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SigningKey.objects.select_related('owner', 'user', 'created_by').all()
        return SigningKey.objects.filter(
            models.Q(owner__contacts__user=user) | 
            models.Q(user=user) |
            models.Q(created_by=user)
        ).distinct().select_related('owner', 'user', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SignatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet solo lectura para registrar y consultar firmas realizadas.
    """
    queryset = Signature.objects.select_related('signing_key', 'signer').all().order_by('-created_at')
    serializer_class = SignatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Signature.objects.select_related('signing_key', 'signer').all().order_by('-created_at')
        return Signature.objects.filter(
            models.Q(signing_key__owner__contacts__user=user) |
            models.Q(signer=user)
        ).distinct().select_related('signing_key', 'signer').order_by('-created_at')


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar documentos a firmar.
    """
    queryset = Document.objects.select_related('company', 'user').all().order_by('-created_at')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Document.objects.select_related('company', 'user').all().order_by('-created_at')
        return Document.objects.filter(
            models.Q(company__contacts__user=user) |
            models.Q(user=user)
        ).distinct().select_related('company', 'user').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_signed(self, request, pk=None):
        document = self.get_object()
        document.status = 'SIGNED'
        document.signed_at = timezone.now()
        document.save(update_fields=['status', 'signed_at'])
        return Response({'status': 'document marked as signed'})

    @action(detail=True, methods=['post'])
    def mark_verified(self, request, pk=None):
        document = self.get_object()
        document.status = 'VERIFIED'
        document.verified_at = timezone.now()
        document.save(update_fields=['status', 'verified_at'])
        return Response({'status': 'document marked as verified'})

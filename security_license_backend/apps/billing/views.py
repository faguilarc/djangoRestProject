from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from .models import PaymentMethod, Invoice, InvoiceItem, Subscription, Payment
from .serializers import PaymentMethodSerializer, InvoiceSerializer, SubscriptionSerializer, PaymentSerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar métodos de pago de usuarios.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PaymentMethod.objects.select_related('user').all()
        return PaymentMethod.objects.filter(user=user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar facturas.
    """
    queryset = Invoice.objects.select_related('company', 'subscription').prefetch_related('items').all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.select_related('company', 'subscription').prefetch_related('items').all().order_by('-created_at')
        return Invoice.objects.filter(
            models.Q(company__contacts__user=user)
        ).distinct().select_related('company', 'subscription').prefetch_related('items').order_by('-created_at')


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar suscripciones recurrentes.
    """
    queryset = Subscription.objects.select_related('company', 'plan').all().order_by('-created_at')
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.select_related('company', 'plan').all().order_by('-created_at')
        return Subscription.objects.filter(
            models.Q(company__contacts__user=user)
        ).distinct().select_related('company', 'plan').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'CANCELED'
        subscription.canceled_at = timezone.now()
        subscription.cancel_at_period_end = True
        subscription.save(update_fields=['status', 'canceled_at', 'cancel_at_period_end'])
        return Response({'status': 'subscription canceled'})

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        subscription = self.get_object()
        # Lógica simple de renovación (en producción sería más compleja)
        subscription.status = 'ACTIVE'
        subscription.cancel_at_period_end = False
        subscription.save(update_fields=['status', 'cancel_at_period_end'])
        return Response({'status': 'subscription renewed'})


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos realizados.
    """
    queryset = Payment.objects.select_related('invoice', 'payment_method').all().order_by('-processed_at')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.select_related('invoice', 'payment_method').all().order_by('-processed_at')
        return Payment.objects.filter(
            models.Q(invoice__company__contacts__user=user)
        ).distinct().select_related('invoice', 'payment_method').order_by('-processed_at')

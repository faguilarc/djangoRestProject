from rest_framework import viewsets, permissions
from .models import PaymentMethod, Invoice, Subscription, Payment
from .serializers import PaymentMethod, InvoiceSerializer, SubscriptionSerializer, PaymentSerializer

# Nota: Hay un conflicto de nombres con el modelo PaymentMethod y el serializer si no se importa bien
from .serializers import PaymentMethodSerializer # Asumiendo que lo creaste en el paso anterior (lo añadí abajo mentalmente)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer # Debes crear este serializer simple en billing/serializers.py
    permission_classes = [permissions.IsAuthenticated]

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.iam.views import UserViewSet, RoleViewSet, MenuViewSet, AuditLogViewSet
from apps.crm.views import CompanyViewSet, ContactViewSet, InteractionViewSet
from apps.licensing.views import PlanViewSet, LicenseViewSet, LicenseActivationViewSet, LicenseUsageViewSet
from apps.signing.views import SigningKeyViewSet, SignatureViewSet, DocumentViewSet
from apps.billing.views import PaymentMethodViewSet, InvoiceViewSet, SubscriptionViewSet, PaymentViewSet

router = DefaultRouter()

# IAM endpoints
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

# CRM endpoints
router.register(r'companies', CompanyViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'interactions', InteractionViewSet)

# Licensing endpoints
router.register(r'plans', PlanViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'license-activations', LicenseActivationViewSet)
router.register(r'license-usage', LicenseUsageViewSet)

# Signing endpoints
router.register(r'signing-keys', SigningKeyViewSet)
router.register(r'signatures', SignatureViewSet)
router.register(r'documents', DocumentViewSet)

# Billing endpoints
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.db import models
from django.utils.translation import gettext_lazy as _

from security_license_backend.apps.core.models import UUIDModel, TimeStampedModel
from security_license_backend.apps.crm.models import Company


class PaymentMethod(UUIDModel, TimeStampedModel):
    """
    Modelo para almacenar métodos de pago de los clientes.
    """
    TYPE_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CRYPTO', 'Cryptocurrency'),
        ('OTHER', 'Other'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='payment_methods',
        verbose_name=_('company'),
        help_text=_('Company that owns this payment method.')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        help_text=_('Type of payment method.')
    )
    provider = models.CharField(
        _('provider'),
        max_length=50,
        help_text=_('Payment provider (e.g., Stripe, PayPal).')
    )
    provider_customer_id = models.CharField(
        _('provider customer ID'),
        max_length=100,
        blank=True,
        help_text=_('Customer ID in the payment provider system.')
    )
    provider_payment_method_id = models.CharField(
        _('provider payment method ID'),
        max_length=100,
        blank=True,
        help_text=_('Payment method ID in the payment provider system.')
    )
    last_four = models.CharField(
        _('last four digits'),
        max_length=4,
        blank=True,
        help_text=_('Last four digits of card or account number.')
    )
    brand = models.CharField(
        _('brand'),
        max_length=50,
        blank=True,
        help_text=_('Card brand or bank name.')
    )
    exp_month = models.PositiveIntegerField(
        _('expiration month'),
        null=True,
        blank=True,
        help_text=_('Expiration month (1-12).')
    )
    exp_year = models.PositiveIntegerField(
        _('expiration year'),
        null=True,
        blank=True,
        help_text=_('Expiration year.')
    )
    is_default = models.BooleanField(
        _('default'),
        default=False,
        help_text=_('Indicates if this is the default payment method.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Indicates if this payment method is active.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        db_table = 'billing_payment_methods'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['provider', 'provider_customer_id']),
        ]

    def __str__(self):
        return f"{self.type} ({self.last_four or '****'}) - {self.company.name}"


class Invoice(UUIDModel, TimeStampedModel):
    """
    Modelo para facturas generadas por suscripciones o compras.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_('company'),
        help_text=_('Company being billed.')
    )
    invoice_number = models.CharField(
        _('invoice number'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Unique invoice number.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text=_('Current status of the invoice.')
    )
    issue_date = models.DateField(
        _('issue date'),
        help_text=_('Date when the invoice was issued.')
    )
    due_date = models.DateField(
        _('due date'),
        help_text=_('Date when the invoice is due.')
    )
    paid_date = models.DateField(
        _('paid date'),
        null=True,
        blank=True,
        help_text=_('Date when the invoice was paid.')
    )
    subtotal = models.DecimalField(
        _('subtotal'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Subtotal before taxes and discounts.')
    )
    tax_rate = models.DecimalField(
        _('tax rate'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Tax rate percentage.')
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Total tax amount.')
    )
    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Discount amount applied.')
    )
    total = models.DecimalField(
        _('total'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Total amount due.')
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD',
        help_text=_('Currency code (ISO 4217).')
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('payment method'),
        help_text=_('Payment method used for this invoice.')
    )
    billing_period_start = models.DateField(
        _('billing period start'),
        null=True,
        blank=True,
        help_text=_('Start date of the billing period.')
    )
    billing_period_end = models.DateField(
        _('billing period end'),
        null=True,
        blank=True,
        help_text=_('End date of the billing period.')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes for the invoice.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )
    pdf_path = models.CharField(
        _('PDF path'),
        max_length=500,
        blank=True,
        help_text=_('Path to the generated PDF invoice.')
    )

    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        db_table = 'billing_invoices'
        ordering = ['-issue_date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['invoice_number']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.company.name}"


class InvoiceItem(UUIDModel, TimeStampedModel):
    """
    Modelo para items individuales dentro de una factura.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('invoice')
    )
    description = models.CharField(
        _('description'),
        max_length=500,
        help_text=_('Description of the item.')
    )
    quantity = models.PositiveIntegerField(
        _('quantity'),
        default=1,
        help_text=_('Quantity of items.')
    )
    unit_price = models.DecimalField(
        _('unit price'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Price per unit.')
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Total amount for this line item.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('invoice item')
        verbose_name_plural = _('invoice items')
        db_table = 'billing_invoice_items'
        ordering = ['id']

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Subscription(UUIDModel, TimeStampedModel):
    """
    Modelo para suscripciones recurrentes a planes.
    """
    STATUS_CHOICES = [
        ('TRIALING', 'Trialing'),
        ('ACTIVE', 'Active'),
        ('PAST_DUE', 'Past Due'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('company'),
        help_text=_('Company with the subscription.')
    )
    plan = models.ForeignKey(
        'licensing.Plan',
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_('plan'),
        help_text=_('Plan being subscribed to.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        help_text=_('Current status of the subscription.')
    )
    provider_subscription_id = models.CharField(
        _('provider subscription ID'),
        max_length=100,
        blank=True,
        help_text=_('Subscription ID in the payment provider system.')
    )
    current_period_start = models.DateTimeField(
        _('current period start'),
        help_text=_('Start date of the current billing period.')
    )
    current_period_end = models.DateTimeField(
        _('current period end'),
        help_text=_('End date of the current billing period.')
    )
    cancel_at_period_end = models.BooleanField(
        _('cancel at period end'),
        default=False,
        help_text=_('Indicates if subscription will cancel at period end.')
    )
    canceled_at = models.DateTimeField(
        _('canceled at'),
        null=True,
        blank=True,
        help_text=_('Date when the subscription was canceled.')
    )
    trial_start = models.DateTimeField(
        _('trial start'),
        null=True,
        blank=True,
        help_text=_('Start date of trial period.')
    )
    trial_end = models.DateTimeField(
        _('trial end'),
        null=True,
        blank=True,
        help_text=_('End date of trial period.')
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions',
        verbose_name=_('payment method'),
        help_text=_('Payment method for recurring payments.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        db_table = 'billing_subscriptions'
        ordering = ['-current_period_end']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'current_period_end']),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.status})"


class Payment(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar pagos realizados.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('company'),
        help_text=_('Company that made the payment.')
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('invoice'),
        help_text=_('Invoice associated with this payment.')
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('subscription'),
        help_text=_('Subscription associated with this payment.')
    )
    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Payment amount.')
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD',
        help_text=_('Currency code (ISO 4217).')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text=_('Status of the payment.')
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments',
        verbose_name=_('payment method'),
        help_text=_('Payment method used.')
    )
    provider_payment_id = models.CharField(
        _('provider payment ID'),
        max_length=100,
        blank=True,
        help_text=_('Payment ID in the payment provider system.')
    )
    processed_at = models.DateTimeField(
        _('processed at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the payment was processed.')
    )
    failure_reason = models.TextField(
        _('failure reason'),
        blank=True,
        help_text=_('Reason for payment failure if applicable.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        db_table = 'billing_payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['invoice', '-created_at']),
        ]

    def __str__(self):
        return f"{self.amount} {self.currency} - {self.company.name} ({self.status})"

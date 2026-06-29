from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel
from apps.iam.models import User
from apps.crm.models import Company


class Plan(UUIDModel, TimeStampedModel):
    """
    Modelo de Plan que define las reglas comerciales.
    Determina límites de usuarios, módulos disponibles y duración.
    """
    BILLING_CYCLE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
        ('LIFETIME', 'Lifetime'),
    ]

    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Unique name for the plan.')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description of the plan features.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Indicates if the plan is available for purchase.')
    )
    max_users = models.PositiveIntegerField(
        _('max users'),
        default=1,
        help_text=_('Maximum number of users allowed.')
    )
    max_licenses = models.PositiveIntegerField(
        _('max licenses'),
        default=1,
        help_text=_('Maximum number of concurrent licenses.')
    )
    duration_days = models.PositiveIntegerField(
        _('duration (days)'),
        default=30,
        help_text=_('Duration of the plan in days (0 for lifetime).')
    )
    billing_cycle = models.CharField(
        _('billing cycle'),
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='MONTHLY',
        help_text=_('Billing cycle for recurring payments.')
    )
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Price per billing cycle.')
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD',
        help_text=_('Currency code (ISO 4217).')
    )
    modules = models.JSONField(
        _('modules'),
        default=list,
        help_text=_('List of module codes included in this plan.')
    )
    features = models.JSONField(
        _('features'),
        default=dict,
        blank=True,
        help_text=_('Additional features and their limits in JSON format.')
    )
    trial_days = models.PositiveIntegerField(
        _('trial days'),
        default=0,
        help_text=_('Number of trial days (0 for no trial).')
    )

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')
        db_table = 'licensing_plans'
        ordering = ['price']
        indexes = [
            models.Index(fields=['is_active', 'billing_cycle']),
        ]

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency})"


class License(UUIDModel, TimeStampedModel):
    """
    Modelo de Licencia que representa una instancia vendida o asignada.
    Contiene la clave de licencia y metadatos de activación.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('SUSPENDED', 'Suspended'),
        ('REVOKED', 'Revoked'),
        ('CANCELLED', 'Cancelled'),
    ]

    license_key = models.CharField(
        _('license key'),
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_('Unique license key (UUID or custom format).')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name=_('company'),
        help_text=_('Company that owns this license.')
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='licenses',
        verbose_name=_('plan'),
        help_text=_('Plan associated with this license.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text=_('Current status of the license.')
    )
    activated_at = models.DateTimeField(
        _('activated at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the license was first activated.')
    )
    starts_at = models.DateTimeField(
        _('starts at'),
        help_text=_('License start date.')
    )
    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('License expiration date.')
    )
    last_validated_at = models.DateTimeField(
        _('last validated at'),
        null=True,
        blank=True,
        help_text=_('Last time the license was validated.')
    )
    validation_count = models.PositiveIntegerField(
        _('validation count'),
        default=0,
        help_text=_('Number of times the license has been validated.')
    )
    max_activations = models.PositiveIntegerField(
        _('max activations'),
        default=1,
        help_text=_('Maximum number of allowed activations.')
    )
    current_activations = models.PositiveIntegerField(
        _('current activations'),
        default=0,
        help_text=_('Current number of active installations.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )
    signature = models.TextField(
        _('signature'),
        blank=True,
        help_text=_('Digital signature of the license data.')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Internal notes about this license.')
    )

    class Meta:
        verbose_name = _('license')
        verbose_name_plural = _('licenses')
        db_table = 'licensing_licenses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['license_key']),
        ]

    def __str__(self):
        return f"{self.license_key} - {self.company.name}"


class LicenseActivation(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar cada activación de una licencia.
    Permite controlar el número de instalaciones simultáneas.
    """
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='activations',
        verbose_name=_('license')
    )
    machine_id = models.CharField(
        _('machine ID'),
        max_length=100,
        help_text=_('Unique identifier of the machine/device.')
    )
    machine_name = models.CharField(
        _('machine name'),
        max_length=200,
        blank=True,
        help_text=_('Friendly name of the machine/device.')
    )
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True,
        help_text=_('IP address from which the activation was made.')
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('User agent string from the activation request.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Indicates if this activation is currently active.')
    )
    deactivated_at = models.DateTimeField(
        _('deactivated at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the activation was deactivated.')
    )
    last_seen_at = models.DateTimeField(
        _('last seen at'),
        null=True,
        blank=True,
        help_text=_('Last time this activation communicated with the server.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata about the activation in JSON format.')
    )

    class Meta:
        verbose_name = _('license activation')
        verbose_name_plural = _('license activations')
        db_table = 'licensing_activations'
        ordering = ['-created_at']
        unique_together = [['license', 'machine_id']]
        indexes = [
            models.Index(fields=['license', 'is_active']),
            models.Index(fields=['machine_id']),
        ]

    def __str__(self):
        return f"{self.license.license_key} - {self.machine_id}"


class LicenseUsage(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar el uso de una licencia.
    Útil para métricas y facturación basada en consumo.
    """
    license = models.ForeignKey(
        License,
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name=_('license')
    )
    metric_name = models.CharField(
        _('metric name'),
        max_length=100,
        help_text=_('Name of the metric being tracked.')
    )
    metric_value = models.BigIntegerField(
        _('metric value'),
        help_text=_('Value of the metric at the time of recording.')
    )
    recorded_at = models.DateTimeField(
        _('recorded at'),
        auto_now_add=True,
        help_text=_('Date and time when the metric was recorded.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('license usage')
        verbose_name_plural = _('license usage records')
        db_table = 'licensing_usage'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['license', 'metric_name', '-recorded_at']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f"{self.license.license_key} - {self.metric_name}: {self.metric_value}"

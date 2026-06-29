from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel
from apps.iam.models import User


class Company(UUIDModel, TimeStampedModel):
    """
    Modelo de Empresa/Cliente para el CRM.
    Centraliza la información de los clientes del sistema.
    """
    STATUS_CHOICES = [
        ('PROSPECT', 'Prospect'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    ]

    name = models.CharField(
        _('company name'),
        max_length=200,
        help_text=_('Legal name of the company.')
    )
    tax_id = models.CharField(
        _('tax ID'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Tax identification number (NIT, RUC, CIF, etc.).')
    )
    email = models.EmailField(
        _('email'),
        help_text=_('Primary contact email for the company.')
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        help_text=_('Primary phone number.')
    )
    website = models.URLField(
        _('website'),
        blank=True,
        help_text=_('Company website URL.')
    )
    industry = models.CharField(
        _('industry'),
        max_length=100,
        blank=True,
        help_text=_('Industry or business sector.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROSPECT',
        help_text=_('Current status of the company in the CRM.')
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_companies',
        verbose_name=_('owner'),
        help_text=_('Sales representative or account owner.')
    )
    address = models.TextField(
        _('address'),
        blank=True,
        help_text=_('Physical address of the company.')
    )
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
        help_text=_('City.')
    )
    state = models.CharField(
        _('state/province'),
        max_length=100,
        blank=True,
        help_text=_('State or province.')
    )
    country = models.CharField(
        _('country'),
        max_length=100,
        default='Unknown',
        help_text=_('Country.')
    )
    postal_code = models.CharField(
        _('postal code'),
        max_length=20,
        blank=True,
        help_text=_('Postal or ZIP code.')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about the company.')
    )

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        db_table = 'crm_companies'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['owner', '-created_at']),
        ]

    def __str__(self):
        return self.name


class Contact(UUIDModel, TimeStampedModel):
    """
    Modelo de Contacto para personas dentro de una empresa.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Undisclosed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name=_('company'),
        help_text=_('Company this contact belongs to.')
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_profile',
        verbose_name=_('user'),
        help_text=_('Linked user account if applicable.')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=100,
        help_text=_('First name.')
    )
    last_name = models.CharField(
        _('last name'),
        max_length=100,
        help_text=_('Last name.')
    )
    email = models.EmailField(
        _('email'),
        help_text=_('Contact email address.')
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        help_text=_('Contact phone number.')
    )
    mobile = models.CharField(
        _('mobile'),
        max_length=20,
        blank=True,
        help_text=_('Mobile phone number.')
    )
    position = models.CharField(
        _('position'),
        max_length=100,
        blank=True,
        help_text=_('Job title or position.')
    )
    department = models.CharField(
        _('department'),
        max_length=100,
        blank=True,
        help_text=_('Department within the company.')
    )
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        help_text=_('Gender.')
    )
    is_primary = models.BooleanField(
        _('primary contact'),
        default=False,
        help_text=_('Indicates if this is the primary contact for the company.')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about the contact.')
    )

    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        db_table = 'crm_contacts'
        ordering = ['last_name', 'first_name']
        unique_together = [['company', 'email']]
        indexes = [
            models.Index(fields=['company', 'is_primary']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company.name})"

    def save(self, *args, **kwargs):
        # Si se marca como primario, desmarcar otros contactos primarios de la misma empresa
        if self.is_primary:
            Contact.objects.filter(company=self.company, is_primary=True).exclude(
                id=self.id
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class Interaction(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar interacciones con contactos o empresas.
    """
    TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('CALL', 'Phone Call'),
        ('MEETING', 'Meeting'),
        ('NOTE', 'Note'),
        ('TASK', 'Task'),
        ('SUPPORT_TICKET', 'Support Ticket'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name=_('company'),
        help_text=_('Company related to this interaction.')
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions',
        verbose_name=_('contact'),
        help_text=_('Specific contact involved in this interaction.')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_interactions',
        verbose_name=_('created by'),
        help_text=_('User who logged this interaction.')
    )
    type = models.CharField(
        _('type'),
        max_length=30,
        choices=TYPE_CHOICES,
        help_text=_('Type of interaction.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='COMPLETED',
        help_text=_('Status of the interaction.')
    )
    subject = models.CharField(
        _('subject'),
        max_length=200,
        blank=True,
        help_text=_('Brief subject or title of the interaction.')
    )
    description = models.TextField(
        _('description'),
        help_text=_('Detailed description of the interaction.')
    )
    scheduled_at = models.DateTimeField(
        _('scheduled at'),
        null=True,
        blank=True,
        help_text=_('Scheduled date and time for the interaction.')
    )
    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('Actual completion date and time.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    class Meta:
        verbose_name = _('interaction')
        verbose_name_plural = _('interactions')
        db_table = 'crm_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['contact', '-created_at']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.type} - {self.subject or self.company.name} ({self.created_at})"

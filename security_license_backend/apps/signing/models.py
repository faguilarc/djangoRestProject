from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel
from apps.iam.models import User
from apps.crm.models import Company


class SigningKey(UUIDModel, TimeStampedModel):
    """
    Modelo para almacenar pares de claves criptográficas por usuario/empresa.
    Las claves privadas se almacenan cifradas usando una clave maestra.
    """
    ALGORITHM_CHOICES = [
        ('ED25519', 'Ed25519'),
        ('RSA_2048', 'RSA 2048'),
        ('RSA_4096', 'RSA 4096'),
    ]

    PURPOSE_CHOICES = [
        ('LICENSE', 'License Signing'),
        ('DOCUMENT', 'Document Signing'),
        ('GENERAL', 'General Purpose'),
    ]

    owner = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='signing_keys',
        verbose_name=_('owner'),
        help_text=_('Company or entity that owns this key pair.')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signing_keys',
        verbose_name=_('user'),
        help_text=_('Specific user associated with this key (optional).')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Friendly name for the key pair.')
    )
    algorithm = models.CharField(
        _('algorithm'),
        max_length=20,
        choices=ALGORITHM_CHOICES,
        default='ED25519',
        help_text=_('Cryptographic algorithm used for this key pair.')
    )
    purpose = models.CharField(
        _('purpose'),
        max_length=20,
        choices=PURPOSE_CHOICES,
        default='GENERAL',
        help_text=_('Intended purpose of this key pair.')
    )
    public_key = models.TextField(
        _('public key'),
        help_text=_('Public key in PEM format.')
    )
    private_key_encrypted = models.TextField(
        _('private key (encrypted)'),
        help_text=_('Private key encrypted with master key in PEM format.')
    )
    fingerprint = models.CharField(
        _('fingerprint'),
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_('SHA-256 fingerprint of the public key.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Indicates if this key pair is currently active.')
    )
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('Optional expiration date for the key pair.')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_signing_keys',
        verbose_name=_('created by'),
        help_text=_('User who created this key pair.')
    )

    class Meta:
        verbose_name = _('signing key')
        verbose_name_plural = _('signing keys')
        db_table = 'signing_keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['fingerprint']),
            models.Index(fields=['purpose', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.algorithm}) - {self.owner.name}"


class Signature(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar cada firma realizada por el sistema.
    Sirve como auditoría y prueba de no repudio.
    """
    TYPE_CHOICES = [
        ('LICENSE', 'License'),
        ('DOCUMENT', 'Document'),
        ('DATA', 'Data'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('PENDING', 'Pending'),
    ]

    signing_key = models.ForeignKey(
        SigningKey,
        on_delete=models.PROTECT,
        related_name='signatures',
        verbose_name=_('signing key'),
        help_text=_('Key pair used to create this signature.')
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_signatures',
        verbose_name=_('signer'),
        help_text=_('User who requested the signature.')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        help_text=_('Type of content being signed.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUCCESS',
        help_text=_('Status of the signing operation.')
    )
    original_hash = models.CharField(
        _('original hash'),
        max_length=64,
        db_index=True,
        help_text=_('SHA-256 hash of the original content.')
    )
    signature_value = models.TextField(
        _('signature value'),
        help_text=_('Digital signature in base64 format.')
    )
    signed_content = models.BinaryField(
        _('signed content'),
        null=True,
        blank=True,
        help_text=_('Original content or reference to it (optional).')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata about the signature in JSON format.')
    )
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True,
        help_text=_('IP address from which the signature was requested.')
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('User agent string from the signature request.')
    )

    class Meta:
        verbose_name = _('signature')
        verbose_name_plural = _('signatures')
        db_table = 'signing_signatures'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['signing_key', '-created_at']),
            models.Index(fields=['original_hash']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['signer', '-created_at']),
        ]

    def __str__(self):
        return f"{self.type} - {self.original_hash[:16]}... ({self.created_at})"


class Document(UUIDModel, TimeStampedModel):
    """
    Modelo opcional para gestionar documentos que pueden ser firmados.
    Permite almacenar metadatos y referencias a archivos.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_SIGNATURE', 'Pending Signature'),
        ('SIGNED', 'Signed'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('company'),
        help_text=_('Company that owns this document.')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Title of the document.')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description of the document.')
    )
    file_path = models.CharField(
        _('file path'),
        max_length=500,
        help_text=_('Path or URL to the stored document file.')
    )
    file_hash = models.CharField(
        _('file hash'),
        max_length=64,
        db_index=True,
        help_text=_('SHA-256 hash of the document file.')
    )
    file_size = models.BigIntegerField(
        _('file size'),
        default=0,
        help_text=_('Size of the document file in bytes.')
    )
    mime_type = models.CharField(
        _('MIME type'),
        max_length=100,
        default='application/octet-stream',
        help_text=_('MIME type of the document.')
    )
    status = models.CharField(
        _('status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text=_('Current status of the document.')
    )
    requires_signature = models.BooleanField(
        _('requires signature'),
        default=True,
        help_text=_('Indicates if the document requires a digital signature.')
    )
    signed_at = models.DateTimeField(
        _('signed at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the document was signed.')
    )
    verified_at = models.DateTimeField(
        _('verified at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the signature was verified.')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata in JSON format.')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('user'),
        help_text=_('Usuario propietario del documento a firmar.'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        db_table = 'signing_documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['status', '-created_at']),
        ]
        unique_together = ('user', 'title')

    def __str__(self):
        return f"{self.title} ({self.status})"

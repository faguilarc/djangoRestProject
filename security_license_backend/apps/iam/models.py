from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para el modelo de usuario.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(UUIDModel, TimeStampedModel, AbstractUser):
    """
    Modelo de Usuario personalizado.
    Usa email como campo único en lugar de username.
    """
    username = None  # Eliminamos username
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        help_text=_('Required. A valid email address.')
    )
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Optional phone number.')
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('Optional user avatar image.')
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Indicates if the user email has been verified.')
    )
    last_login_at = models.DateTimeField(
        _('last login at'),
        null=True,
        blank=True,
        help_text=_('Date and time of the last login.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email ya es requerido por defecto

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Actualizar last_login_at si es necesario
        if self.last_login is not None and self.last_login_at is None:
            self.last_login_at = self.last_login
        super().save(*args, **kwargs)


class Role(UUIDModel, TimeStampedModel):
    """
    Modelo de Rol para agrupar permisos.
    Similar a Django Group pero con más funcionalidades.
    """
    name = models.CharField(
        _('name'),
        max_length=150,
        unique=True,
        help_text=_('Unique name for the role.')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description of the role and its purpose.')
    )
    is_system = models.BooleanField(
        _('system role'),
        default=False,
        help_text=_('System roles cannot be deleted or modified.')
    )
    permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles',
        help_text=_('Permissions assigned to this role.')
    )

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        db_table = 'iam_roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserRoles(UUIDModel, TimeStampedModel):
    """
    Modelo intermedio para la relación muchos-a-muchos entre User y Role.
    Permite añadir metadata a la asignación de roles.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('user')
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('role')
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name=_('assigned by'),
        help_text=_('User who assigned this role.')
    )
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('Optional expiration date for this role assignment.')
    )

    class Meta:
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
        db_table = 'iam_user_roles'
        unique_together = [['user', 'role']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class Menu(UUIDModel, TimeStampedModel):
    """
    Modelo de Menú para la estructura de navegación de la aplicación.
    Soporta jerarquía (menús padre/hijo).
    """
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent menu'),
        help_text=_('Parent menu item for hierarchical structure.')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Display name of the menu item.')
    )
    icon = models.CharField(
        _('icon'),
        max_length=50,
        blank=True,
        help_text=_('Icon class or name for the menu item.')
    )
    url = models.CharField(
        _('url'),
        max_length=200,
        blank=True,
        help_text=_('URL or route path for the menu item.')
    )
    order = models.PositiveIntegerField(
        _('order'),
        default=0,
        help_text=_('Order of the menu item within its parent.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Indicates if the menu item is visible.')
    )
    required_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('required permissions'),
        blank=True,
        related_name='menus',
        help_text=_('Permissions required to view this menu item.')
    )

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
        db_table = 'iam_menus'
        ordering = ['parent__order', 'order']

    def __str__(self):
        return self.name


class AuditLog(UUIDModel, TimeStampedModel):
    """
    Modelo para registrar actividades del sistema (auditoría).
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PERMISSION_CHANGE', 'Permission Change'),
        ('ROLE_ASSIGN', 'Role Assign'),
        ('LICENSE_GENERATE', 'License Generate'),
        ('LICENSE_VALIDATE', 'License Validate'),
        ('DOCUMENT_SIGN', 'Document Sign'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('user')
    )
    action = models.CharField(
        _('action'),
        max_length=50,
        choices=ACTION_CHOICES,
        help_text=_('Type of action performed.')
    )
    resource_type = models.CharField(
        _('resource type'),
        max_length=100,
        help_text=_('Type of resource affected (e.g., User, License, Document).')
    )
    resource_id = models.UUIDField(
        _('resource id'),
        null=True,
        blank=True,
        help_text=_('ID of the affected resource.')
    )
    ip_address = models.GenericIPAddressField(
        _('ip address'),
        null=True,
        blank=True,
        help_text=_('IP address from which the action was performed.')
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('User agent string from the request.')
    )
    details = models.JSONField(
        _('details'),
        default=dict,
        blank=True,
        help_text=_('Additional details about the action in JSON format.')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILURE', 'Failure'),
            ('PENDING', 'Pending'),
        ],
        default='SUCCESS',
        help_text=_('Status of the action.')
    )

    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        db_table = 'iam_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.resource_type} ({self.created_at})"

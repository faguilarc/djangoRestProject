from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que añade campos de created_at y updated_at
    a todos los modelos que lo hereden.
    """
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the record was created.')
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Date and time when the record was last updated.')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """
    Manager que excluye automáticamente los registros eliminados lógicamente.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager):
    """
    Manager que incluye todos los registros, incluso los eliminados lógicamente.
    """
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que añade eliminación lógica (soft delete).
    """
    deleted_at = models.DateTimeField(
        _('deleted at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the record was soft deleted.')
    )

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Sobrescribe el método delete para hacer soft delete.
        """
        from django.utils import timezone
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
        return self

    def hard_delete(self, using=None, keep_parents=False):
        """
        Método para eliminar físicamente el registro.
        """
        return super().delete(using=using, keep_parents=keep_parents)


class UUIDModel(models.Model):
    """
    Modelo abstracto que añade un campo UUID como primary key.
    """
    import uuid
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )

    class Meta:
        abstract = True

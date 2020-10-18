import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangoapps.erp.signals import state_changed


class OrderingMixin(models.Model):
    """Using for https://django-admin-sortable2.readthedocs.io/"""
    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name=_('#'),
    )

    class Meta:
        ordering = ['ordering']
        abstract = True


class ByCodeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class CodeNaturalKeyAbstractModel(models.Model):
    code = models.SlugField(max_length=200, default=uuid.uuid4, unique=True, verbose_name=_('Code'))

    objects = ByCodeManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.code,)


class CreatedUpdatedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    class Meta:
        abstract = True


class StatefulMixin(models.Model):
    """Triggers state signal on update of state. Derives should redefine state field."""

    state = models.CharField(max_length=200, null=True, blank=True)

    def set_state(self, new_state):
        """Besides saving state it notifies all interested partners about it."""
        self.state = new_state
        self.save()

    def _notify_state_change(self, old_state):
        # send signal
        state_changed.send(sender=self.__class__, old_state=old_state, instance=self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        old = self.__class__.objects.filter(pk=self.pk).first()
        old_state = old.state if old else None

        super().save(force_insert, force_update, using, update_fields)

        if old_state != self.state:
            self._notify_state_change(old_state=old_state)

    class Meta:
        abstract = True
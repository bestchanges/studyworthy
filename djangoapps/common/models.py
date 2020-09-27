import uuid

from django.db import models
from django.db.models import Field
from django.utils import timezone

from .signals import state_changed


class Document(models.Model):
    document_number_template = 'D-{number_total}'
    document_number = models.CharField(max_length=200, blank=True, null=True)
    document_date = models.DateField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # document_applicable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def notify_state_change(self, child_model: 'Document', old_state):
        pass

    def set_state(self, new_state):
        """Besides saving state it notifies all interested partners about it."""
        self.state = new_state
        self.save()

    def _notify_state_change(self, old_state):
        # send signal to everybody
        state_changed.send(sender=self.__class__, old_state=old_state, instance=self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create = self.pk is None

        # detect state change
        if not is_create:
            old = self.__class__.objects.get(pk=self.pk)
            old_state = old.state
        else:
            old_state = None

        if is_create and not self.document_number:
            self.document_number = self._generate_document_number()
        super().save(force_insert, force_update, using, update_fields)

        if old_state != self.state:
            self._notify_state_change(old_state=old_state)


    def _generate_document_number(self):
        template = self.document_number_template
        if not self.document_date:
            self.document_date = timezone.now().date()
        today_start = self.document_date
        month_start = today_start.replace(day=1)
        year_start = month_start.replace(month=1)
        number = template.format(
            number_today=self.__class__.objects.filter(document_date__gte=today_start).count() + 1,
            number_month=self.__class__.objects.filter(document_date__gte=month_start).count() + 1,
            number_year=self.__class__.objects.filter(document_date__gte=year_start).count() + 1,
            number_total=self.__class__.objects.all().count() + 1,
        )
        return number

    def __str__(self):
        return f'{self.document_number} at {self.document_date}'

    class Meta:
        abstract = True

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoapps.lms.models.base import Person


class SiteUser(AbstractUser):
    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE)


@receiver(post_save, sender=SiteUser)
def on_user_create(sender, instance: SiteUser, created, **kwargs):
    if created:
        try:
            person = Person.objects.get(email=instance.email)
            if instance.first_name and not person.first_name:
                person.first_name = instance.first_name
                person.save()
            if instance.last_name and not person.last_name:
                person.last_name = instance.last_name
                person.save()
        except ObjectDoesNotExist:
            person = Person.objects.create(
                code=instance.username,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
            )
        instance.person = person
        instance.save()

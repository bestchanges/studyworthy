"""
The most common root models. They are used by most of other models
"""
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from lms import config


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


class ByCodeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class CodeNaturalKeyAbstractModel(models.Model):
    code = models.CharField(max_length=36, unique=True)

    objects = ByCodeManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.code,)


class Person(CodeNaturalKeyAbstractModel):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(null=True, unique=True)  # TODO: can we use unique=True for nullable ?
    phone = models.CharField(max_length=20, default='', blank=True)
    skype = models.CharField(max_length=100, default='', blank=True)
    google_account = models.CharField(max_length=200, default='', blank=True)
    github_account = models.CharField(max_length=200, default='', blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default='ru')
    country = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in config.TIMEZONES], default=settings.TIME_ZONE)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.get_full_name()} {self.email}'


class UserPerson(AbstractUser):
    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE)


@receiver(post_save, sender=UserPerson)
def on_user_create(sender, instance: UserPerson, created, **kwargs):
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


class Author(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Author: {self.person.get_full_name()}'

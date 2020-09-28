"""
The most common root models. They are used by most of other models
"""
import uuid

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.db import models
from natural_keys import NaturalKeyModel

from djangoapps.lms import config


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


class ByCodeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class CodeNaturalKeyAbstractModel(models.Model):
    code = models.CharField(max_length=200, unique=True)

    objects = ByCodeManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.code,)


class Person(NaturalKeyModel):
    code = models.SlugField(max_length=100, default=uuid.uuid4, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(null=True, unique=True)  # TODO: can we use unique=True for nullable ?
    phone = models.CharField(max_length=20, default='', blank=True)
    skype = models.CharField(max_length=100, default='', blank=True)
    google_account = models.CharField(max_length=200, default='', blank=True)
    github_account = models.CharField(max_length=200, default='', blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default='ru')
    country = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in config.TIMEZONES], default=settings.TIME_ZONE)
    is_admin = models.BooleanField(default=False)
    can_teach = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.full_name} {self.email}'

    @classmethod
    def lookup_by_email(cls, email):
        return cls.objects.filter(email__iexact=email).first()


class Author(NaturalKeyModel):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.person.full_name


class Teacher(NaturalKeyModel):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, unique=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.person.full_name



class Student(NaturalKeyModel):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.person.full_name


class Admin(NaturalKeyModel):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.person.full_name


from django.db import models
from django.core.validators import MinLengthValidator, validate_email


class AbstractUser(models.Model):
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('en', 'English'),
        ('ua', 'Ukrainian')
    ]

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    country_name = models.CharField(max_length=30, )
    city_name = models.CharField(max_length=30)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    skype = models.CharField(max_length=32, validators=[MinLengthValidator])
    email = models.CharField(max_length=32, validators=[validate_email])
    phone = models.CharField(max_length=30)

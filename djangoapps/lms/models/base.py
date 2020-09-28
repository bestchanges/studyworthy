"""
The most common root models. They are used by most of other models
"""

from django.db import models
from natural_keys import NaturalKeyModel

from djangoapps.erp.models import Person


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

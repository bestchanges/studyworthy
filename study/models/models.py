"""
All other models.
"""
from django.db import models

from study.models.base import Person
from study.models.content import Course
from study.models.learning import Learning


class ApplicationForm(models.Model):
    learning = models.ForeignKey(Learning, on_delete=models.PROTECT, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    comment = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

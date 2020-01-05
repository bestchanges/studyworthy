"""
All other models.
"""
from django.db import models

from lms.models.base import Person
from lms.models.content import Course
from lms.models.learning import Learning


class ApplicationForm(models.Model):
    learning = models.ForeignKey(Learning, on_delete=models.PROTECT, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    comment = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

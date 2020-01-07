from django.db import models

from crm.models.erp_models import Product
from lms.models.content import Course


class CourseProduct(Product):
    items = models.ManyToManyField(Course)
    short_description = models.CharField(max_length=250, null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

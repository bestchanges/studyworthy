from django.db import models

from crm.models.erp_models import Product
from lms.models.base import Person
from lms.models.content import Course
from lms.models.learning import Learning


class CourseProduct(Product):
    class Level(models.IntegerChoices):
        BEGINNER = 1
        EASY = 2
        MEDIUM = 3
        EXPERT = 4

    items = models.ManyToManyField(Course)
    short_description = models.CharField(max_length=250, null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    level = models.IntegerField(choices=Level.choices, null=True, blank=True)
    number_of_lessons = models.IntegerField()
    number_of_tasks = models.IntegerField()
    number_of_video_materials = models.IntegerField()
    duration = models.CharField(max_length=100, null=True, blank=True, help_text="Например \"3 мес 2 недели\"")
    goals = models.TextField(
        null=True, blank=True,
        help_text="Что студент будет уметь после прохождения курса. Буллеты будут оформлены отдельно."
    )


class Enrollment(models.Model):
    class State(models.TextChoices):
        NEW = 'new'
        WAITING = 'waiting'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'

    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

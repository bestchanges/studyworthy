import logging
from django.db import models

from djangoapps.crm.models.erp_models import Product, ClientOrder
from djangoapps.lms.models.content import Course

logger = logging.getLogger(__name__)


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
    # TODO: extract as @properties
    number_of_lessons = models.IntegerField(null=True, blank=True)
    number_of_tasks = models.IntegerField(null=True, blank=True)
    number_of_video_materials = models.IntegerField(null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True, help_text="Например \"3 мес 2 недели\"")
    goals = models.TextField(
        null=True, blank=True,
        help_text="Что студент будет уметь после прохождения курса"
    )

    def enroll_from_client_order(self, client_order: ClientOrder):
        logger.info(f'Enrolling from {client_order}')
        # create client
        # optionally create user
        # map order, invoice, payments to the person


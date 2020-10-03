import logging

from django.contrib.auth.models import User
from django.db import models

from djangoapps.erp.enums import IntegerChoices
from djangoapps.erp.models import Product, ClientOrder
from djangoapps.lms.models.lms_models import Course, Student
from djangoapps.lms_cms.logic.users import create_lms_user

logger = logging.getLogger(__name__)


class CourseProduct(Product):
    class Level(IntegerChoices):
        BEGINNER = 1
        EASY = 2
        MEDIUM = 3
        EXPERT = 4

    courses = models.ManyToManyField(Course)
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

    def __str__(self):
        return f'{self.name} ({self.price})'

    def enroll_from_client_order(self, client_order: ClientOrder):
        logger.info(f'Enrolling from {client_order}')

        # create client
        person = client_order.client
        if not person.user:
            # try to match by email
            user = User.objects.filter(username__iexact=person.email).first()
            if not user:
                logger.info(f'User {person.email} not found. Create new')
                # optionally create user
                user = create_lms_user(
                    email=person.email,
                    first_name=person.first_name,
                    last_name=person.last_name,
                    send_email=True,
                )
            assert user
            person.user = user
            person.save()

        for course in self.courses.all():
            # create flow for personal use. For group flows need to save flow in ProductOrderItem
            flow = course.create_flow()
            logger.info(f'Created flow {flow} for course {course}')
            # assign Student to this flow
            student = Student.objects.create(
                user=person.user,
                flow=flow,
                role=Student.ROLE_STUDENT,
            )
            logger.info(f'Created student {student}')

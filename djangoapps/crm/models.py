import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from djangoapps.erp.enums import IntegerChoices
from djangoapps.erp.models import Product, Order, Person, DigitalProduct , Organization, Payment
from djangoapps.lms.models.lms_models import Course, Student
from djangoapps.lms_cms.logic.users import create_lms_user

logger = logging.getLogger(__name__)

_MY_ORG = None

def my_organization():
    """Return my organization. Do not forget to initialize organization"""
    global _MY_ORG
    if not _MY_ORG:
        _MY_ORG = Organization.objects.get(code=settings.MY_ORGANIZATION_CODE)
    return _MY_ORG


class CourseProduct(DigitalProduct):
    class Level(IntegerChoices):
        BEGINNER = 1
        EASY = 2
        MEDIUM = 3
        EXPERT = 4

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=250, default='', blank=True)
    long_description = models.TextField(default='', blank=True)
    level = models.IntegerField(choices=Level.choices, null=True, blank=True)
    # TODO: extract as @properties
    number_of_lessons = models.IntegerField(null=True, blank=True)
    number_of_tasks = models.IntegerField(null=True, blank=True)
    number_of_video_materials = models.IntegerField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, help_text="Продолжительность обучения. Формат: DDD HH:MM:SS")
    goals = models.TextField(
        null=True, blank=True,
        help_text="Что студент будет уметь после окончании курса"
    )

    def __str__(self):
        return f'{self.name} ({self.price})'

    def enroll_from_client_order(self, order: Order):
        logger.info(f'Enrolling from {order}')

        person = order.buyer.person
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

        # create flow for personal use. For group flows need to save flow in ProductOrderItem
        flow = self.course.create_flow()
        logger.info(f'Created flow {flow} for course {self.course}')
        # assign Student to this flow
        student = Student.objects.create(
            user=person.user,
            flow=flow,
            role=Student.ROLE_STUDENT,
        )
        logger.info(f'Created student {student}')

from django.db import models

from djangoapps.crm.models.erp_models import Product, ClientOrder
from djangoapps.lms.models.content import Course

def enroll_student(client_order: ClientOrder):
    print('HELLO STUDENT!!!!')
    pass

ACTIONS = {
    ClientOrder: {
        'ENROLL': {
            'action_name': 'Enroll student',
            'method': enroll_student
        },
    }
}

def action_choices_for_class(cls):
    result = []
    for action_code, action in ACTIONS.get(cls, {}).items():
        result.append([
            action_code,
            action['action_name'],
        ])
    return result


def get_action_method_by_code(cls, action_code):
    class_actions = ACTIONS.get(cls, {})
    method = class_actions.get(action_code, {}).get('method')
    return method


class CourseProduct(Product):
    class Actions(models.TextChoices):
        ENROLL = 'ENROLL'

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
    on_order_new = models.CharField(max_length=100, choices=action_choices_for_class(ClientOrder), null=True, blank=True)
    on_invoice_payed = models.CharField(max_length=100, choices=action_choices_for_class(ClientOrder), null=True, blank=True)

from django.test import TestCase, Client
from django.urls import reverse

from study.models.content import Course
from study.models.learning import Learning


class ViewsModels(TestCase):
    fixtures = ['fixtures/sample-persons.yaml', 'fixtures/sample-course.yaml']

    def test_learning_creates_lessons(self):
        course = Course.objects.get_by_natural_key('hp')
        number_of_units = 1
        assert course.unit_set.count() == number_of_units
        learning = Learning(course=course)
        learning.save()
        assert learning.lesson_set.count() == number_of_units, "units == lessons"

import random

from django.apps import apps
from django.test import TestCase

from djangoapps.lms.apps import LmsConfig
from djangoapps.lms.models.lms_models import Course, Lesson, Unit


class ModelsTestCase(TestCase):

    def test_course_unit_lessons(self):
        course = Course.objects.create(title='test course')
        unit_1 = Unit.objects.create(name='test unit', course=course)
        unit_2 = Unit.objects.create(name='test unit 2', course=course)
        unit_3 = Unit.objects.create(name='test unit 3', course=course)
        self.assertEqual('test unit', course.units.first().name)
        self.assertEqual('test unit 3', course.units.last().name)
        for number in range(10):
            lesson = Lesson.objects.create(title=f'lesson {number+1}', )
            course.add_lesson(lesson, unit=random.choice(course.units.all()))
        self.assertEqual(10, course.course_lessons.count())
        course_lessons_first = course.course_lessons.first()
        course_lessons_last = course.course_lessons.last()
        self.assertEqual(1, course_lessons_first.ordering)
        self.assertEqual('lesson 1', course_lessons_first.lesson.title)

        self.assertEqual(10, course_lessons_last.ordering)
        self.assertEqual('lesson 10', course_lessons_last.lesson.title)

    def test_apps(self):
        self.assertEqual(LmsConfig.name, 'djangoapps.lms')
        self.assertEqual(apps.get_app_config('lms').name, 'djangoapps.lms')

    def test_flow(self):
        course = Course.objects.create(title='test course')
        for number in range(7):
            lesson = Lesson.objects.create(title=f'lesson {number+1}', )
            course.add_lesson(lesson)

        flow = course.create_flow()
        self.assertEqual(flow.flow_lessons.count(), 7, "Lessons must be copied from course")
        self.assertEqual('lesson 1', flow.flow_lessons.first().lesson.title)
        self.assertEqual('lesson 7', flow.flow_lessons.last().lesson.title)

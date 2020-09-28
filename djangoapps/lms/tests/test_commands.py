"""
Test custom commands for manage.py
"""
import os
import unittest
from io import StringIO

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from djangoapps.lms.models.content import Course, Unit
from djangoapps.lms.models.learning import Learning



class TestCommands(TestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(
            code='hpi',
            title='Course title',
            state=Course.State.ACTIVE,
            short_description='Sample course',
            long_description='Hello Python header',
        )
        self.unit1 = Unit.objects.create(
            code='unit1',
            name='Intro',
            course=self.course,
            order=1,
        )
        self.unit1 = Unit.objects.create(
            code='unit-2',
            name='Sceond',
            course=self.course,
            order=2,
        )
        self.unit1 = Unit.objects.create(
            code='unit-3',
            name='Third',
            course=self.course,
            order=3,
        )

    def test_command_periodic(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test')
        learning.save()
        out = StringIO()
        call_command('periodic', stdout=out)
        self.assertIn('Done', out.getvalue())

    def test_command_periodic_do_job(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test_command_do_tasks')
        learning.start_planned_at = timezone.now() - timezone.timedelta(hours=5)
        learning.save()
        num_lessons = learning.lesson_set.count()
        for lesson in learning.lesson_set.all():
            lesson.open_planned_at = timezone.now() - timezone.timedelta(hours=3)
            lesson.save()
        out = StringIO()

        call_command('periodic', stdout=out)

        self.assertIn(f'Started Learnings: 1', out.getvalue())
        self.assertIn(f'Opened Lessons: {num_lessons}', out.getvalue())

    BASE_DIR = os.path.dirname(__file__)
    YAML_FILE = os.path.join(BASE_DIR, 'course.yaml')

    @unittest.skip('not supported')
    def test_command_importcourse_fail_without_argument(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command('importcourse', stdout=out)

    @unittest.skip('not supported')
    def test_command_importcourse_do_job(self):
        out = StringIO()
        call_command('importcourse', self.YAML_FILE, stdout=out)
        self.assertIn('Done', out.getvalue())

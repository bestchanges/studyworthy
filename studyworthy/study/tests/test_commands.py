from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from study.models.content import Course
from study.models.learning import Learning


class TestCommands(TestCase):
    fixtures = ['fixtures/sample-course-hpi.yaml']

    def test_command_output(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test')
        learning.save()
        out = StringIO()
        call_command('periodic', stdout=out)
        self.assertIn('Done', out.getvalue())

    def test_command_do_tasks(self):
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

import datetime

import pytz
from django.test import TestCase
from django.utils import timezone

from study.models.content import Course
from study.models.learning import Learning


class TestModels(TestCase):
    fixtures = ['fixtures/sample-persons.yaml', 'fixtures/sample-course-hpi.yaml']

    def test_learning_creates_lessons(self):
        course = Course.objects.get_by_natural_key('hpi')
        number_of_units = 3
        assert course.unit_set.count() == number_of_units
        learning = Learning(course=course)
        learning.save()
        assert learning.lesson_set.count() == number_of_units, "units == lessons"

    def test_learning_reschedule(self):
        course = Course.objects.get_by_natural_key('hpi')
        number_of_units = 3
        assert course.unit_set.count() == number_of_units
        learning = Learning(course=course, )
        learning.save()
        for lesson in learning.lesson_set.all():
            self.assertEqual(lesson.open_planned_at, None, "Lessons shall not be planned on create")

        learning_timezone = 'Europe/Paris'
        learning.timezone = learning_timezone
        learning.start_planned_at = datetime.datetime(2020, 1, 4, tzinfo=pytz.utc)
        timezone.now()
        learning.schedule='Mon 13:00, Wed 16:00'
        learning.save()

        learning.reschedule()

        lessons = list(learning.lesson_set.all())
        for lesson in lessons:
            self.assertNotEqual(lesson.open_planned_at, None, "Lessons shall BE planned after reschedule")
        self.assertEqual(lessons[0].open_planned_at, datetime.datetime(2020, 1, 6, 12, tzinfo=pytz.utc))
        self.assertEqual(lessons[1].open_planned_at, datetime.datetime(2020, 1, 8, 15, tzinfo=pytz.utc))
        self.assertEqual(lessons[2].open_planned_at, datetime.datetime(2020, 1, 13, 12, tzinfo=pytz.utc))

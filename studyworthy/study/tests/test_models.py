import datetime

import pytz
from django.test import TestCase
from django.utils import timezone

from study import signals
from study.models.content import Course
from study.models.learning import Learning, Lesson
from study.signals import learning_started_signal, learning_finished_signal, lesson_opened_signal


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

    def test_send_learning_started_signal(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test_send_learning_started_signal')
        learning.save()
        self.assertNotEqual(learning.state, learning.State.ONGOING)
        received_flag = False

        def receiver_function(sender, learning, signal):
            nonlocal received_flag
            received_flag = True
            assert isinstance(learning, Learning)
        signals.learning_started_signal.connect(receiver_function)
        learning.state = learning.State.ONGOING
        learning.save()

        self.assertTrue(received_flag)
        learning_started_signal.disconnect(receiver_function)

    def test_send_learning_finished_signal(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test_send_learning_finished_signal', state=Learning.State.ONGOING)
        learning.save()
        self.assertEqual(learning.state, learning.State.ONGOING)
        received_flag = False

        def receiver_function(sender, learning, signal):
            nonlocal received_flag
            received_flag = True
            assert isinstance(learning, Learning)
        learning_finished_signal.connect(receiver_function)
        learning.state = learning.State.FINISHED
        learning.save()

        self.assertTrue(received_flag)
        learning_finished_signal.disconnect(receiver_function)

    def test_send_lesson_opened_signal(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test_send_learning_finished_signal', state=Learning.State.ONGOING)
        learning.save()
        lesson = learning.lesson_set.first()
        self.assertEqual(lesson.state, Lesson.State.CLOSED)
        received_flag = False

        def receiver_function(sender, lesson, signal):
            nonlocal received_flag
            received_flag = True
            assert isinstance(lesson, Lesson)
        lesson_opened_signal.connect(receiver_function)

        lesson.state = Lesson.State.OPENED
        lesson.save()

        self.assertTrue(received_flag)
        lesson_opened_signal.disconnect(receiver_function)

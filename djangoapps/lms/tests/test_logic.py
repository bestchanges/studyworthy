from django.test import TestCase
from django.utils import timezone

from lms.logic import periodic_task_start_learnings, periodic_task_open_lessons
from lms.models.content import Course
from lms.models.learning import Learning, Lesson


class TestModels(TestCase):
    fixtures = ['sample-course-hpi.yaml']

    def test_periodic_task_start_learnings(self):
        course = Course.objects.get_by_natural_key('hpi')
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        two_days_in_future = timezone.now() + timezone.timedelta(days=2)
        data_sets = (
            [one_hour_ago, Learning.State.ONGOING],
            [two_days_in_future, Learning.State.PLANNED],
            [two_days_ago, Learning.State.PLANNED],
        )

        for entry in data_sets:
            date = entry[0]
            learning = Learning(course=course, start_planned_at=date, code=str(date))
            learning.save()
            entry.append(learning)
            self.assertEqual(learning.state, learning.State.PLANNED)

        periodic_task_start_learnings()

        for entry in data_sets:
            date, expected_state, learning = entry
            learning = Learning.objects.get(pk=learning.id)
            self.assertEqual(learning.state, expected_state, f"For date={date} state shall be {expected_state}, but actual was {learning.state}")

    def test_periodic_task_open_lessons(self):
        course = Course.objects.get_by_natural_key('hpi')
        learning = Learning(course=course, code='test_periodic_task_open_lessons')
        learning.save()
        self.assertGreaterEqual(learning.lesson_set.count(), 3)

        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        two_days_ago = timezone.now() - timezone.timedelta(days=2)
        two_days_in_future = timezone.now() + timezone.timedelta(days=2)
        data_sets = (
            [one_hour_ago, Lesson.State.OPENED],
            [two_days_in_future, Lesson.State.CLOSED],
            [two_days_ago, Lesson.State.CLOSED],
        )

        for lesson, entry in zip(learning.lesson_set.all(), data_sets):
            date = entry[0]
            self.assertEqual(lesson.state, Lesson.State.CLOSED)
            lesson.open_planned_at = date
            lesson.save()

        periodic_task_open_lessons()

        for lesson, entry in zip(learning.lesson_set.all(), data_sets):
            date, expected_state = entry
            self.assertEqual(lesson.state, expected_state, f"For date={date} state shall be {expected_state}, but actual was {lesson.state}")

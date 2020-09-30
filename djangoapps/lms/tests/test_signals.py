from django.test import TestCase

from django.test import TestCase

from djangoapps.lms.models.lms_models import Course, Flow, Lesson, FlowLesson
from djangoapps.lms.signals import lesson_available, lesson_unavailable


class ModelsTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(title='test course')
        self.lessons = []
        for number in range(10):
            self.lessons.append(Lesson.objects.create(
                course=self.course,
                title=f'lesson {number}',
            ))
        self.lesson_available_caught = 0
        self.lesson_unavailable_caught = 0
        lesson_available.connect(self.on_lesson_available)
        lesson_unavailable.connect(self.on_lesson_unavailable)

    def tearDown(self) -> None:
        lesson_available.disconnect(self.on_lesson_available)
        lesson_unavailable.disconnect(self.on_lesson_unavailable)

    def on_lesson_available(self, sender, flow_lesson, **kwargs):
        self.lesson_available_caught += 1

    def on_lesson_unavailable(self, sender, flow_lesson, **kwargs):
        self.lesson_unavailable_caught += 1

    def test_open_close_flow_lesson_send_signals(self):
        flow = Flow.objects.create(course=self.course, name='flow 1')
        flow_lesson: FlowLesson = flow.flow_lessons.first()

        self.assertFalse(flow_lesson.is_opened)
        self.assertFalse(flow_lesson.opened_at)

        flow_lesson.open_lesson()
        self.assertTrue(flow_lesson.is_opened)
        self.assertTrue(flow_lesson.opened_at)
        self.assertEqual(self.lesson_available_caught, 1)
        self.assertEqual(self.lesson_unavailable_caught, 0)

        # duplicate open
        flow_lesson.open_lesson()
        self.assertTrue(flow_lesson.is_opened)
        self.assertTrue(flow_lesson.opened_at)
        self.assertEqual(self.lesson_available_caught, 1)
        self.assertEqual(self.lesson_unavailable_caught, 0)

        flow_lesson.close_lesson()
        self.assertFalse(flow_lesson.is_opened)
        self.assertEqual(self.lesson_available_caught, 1)
        self.assertEqual(self.lesson_unavailable_caught, 1)

        # duplicate close
        flow_lesson.close_lesson()
        self.assertFalse(flow_lesson.is_opened)
        self.assertEqual(self.lesson_available_caught, 1)
        self.assertEqual(self.lesson_unavailable_caught, 1)



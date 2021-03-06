from django.test import TestCase
from django.utils.timezone import now

from djangoapps.lms.models import Course, Unit, Lesson, Student, Flow, FlowLesson, ParticipantLesson
from djangoapps.lms_cms import app_init
from djangoapps.lms_cms.tests.utils import create_student_user


class UnitTestCase(TestCase):
    def setUp(self) -> None:
        app_init.init()
        course = Course.objects.create(title='Test course')
        unit_1 = Unit.objects.create(name='First unit', course=course)
        unit_2 = Unit.objects.create(name='Second unit', course=course)
        self.lesson_1 = Lesson.objects.create(title='L1')
        self.lesson_2 = Lesson.objects.create(title='L2')
        self.lesson_3 = Lesson.objects.create(title='L3')
        self.lesson_4 = Lesson.objects.create(title='L4')
        course.add_lesson(self.lesson_1, unit_1)
        course.add_lesson(self.lesson_2, unit_2)
        course.add_lesson(self.lesson_3, unit_2)
        course.add_lesson(self.lesson_4)
        self.course = course
        self.unit_1 = unit_1
        self.unit_2 = unit_2

    def test_lessons_group_by_units(self):
        """
        Target: to get list of {'unit':Unit, 'lessons': [Lesson,Lesson]}.

        At first entry should go lessons without Unit (Unit == None).
        """
        lessons_by_unit = self.course.lessons_by_unit()
        expected = (
            (self.unit_1, [self.lesson_1]),
            (self.unit_2, [self.lesson_2, self.lesson_3]),
            (None, [self.lesson_4]),
        )
        for pair_expected, pair_real in zip(expected, lessons_by_unit.items()):
            unit_1, lessons_1 = pair_expected
            unit_2, course_lessons_2 = pair_real
            self.assertEqual(unit_1, unit_2)
            lessons_2 = [course_lesson.lesson for course_lesson in course_lessons_2]
            self.assertEqual(lessons_1, lessons_2)

    def test_skipped_lesson(self):
        """
        Skipped means that this lesson has not been completed yet and
        there is at least one available subsequent lesson.
        """
        # lesson 1 is available and completed
        # lesson 2 is available and is not completed
        # lesson 3 is available and is not completed
        # lesson 4 is not available
        flow = Flow.objects.create(course=self.course)
        user = create_student_user()
        student = Student.objects.create(flow=flow, user=user)
        flow_lesson_1 = FlowLesson.objects.get(flow=flow, lesson=self.lesson_1)
        flow_lesson_2 = FlowLesson.objects.get(flow=flow, lesson=self.lesson_2)
        flow_lesson_3 = FlowLesson.objects.get(flow=flow, lesson=self.lesson_3)
        flow_lesson_4 = FlowLesson.objects.get(flow=flow, lesson=self.lesson_4)
        participant_lesson_1 = ParticipantLesson.objects.get(flow_lesson=flow_lesson_1, participant=student)
        participant_lesson_2 = ParticipantLesson.objects.get(flow_lesson=flow_lesson_2, participant=student)
        participant_lesson_3 = ParticipantLesson.objects.get(flow_lesson=flow_lesson_3, participant=student)
        participant_lesson_4 = ParticipantLesson.objects.get(flow_lesson=flow_lesson_4, participant=student)
        flow_lesson_1.is_opened = True; flow_lesson_1.save()
        flow_lesson_2.is_opened = True; flow_lesson_2.save()
        flow_lesson_3.is_opened = True; flow_lesson_3.save()
        flow_lesson_4.is_opened = False; flow_lesson_4.save()
        participant_lesson_1.when_completed = now(); participant_lesson_1.save()
        # lesson_2 must be marked as missed
        participant_lessons = student.list_lessons_marked_missed()
        self.assertEqual(participant_lessons[0], participant_lesson_1)
        self.assertEqual(participant_lessons[1], participant_lesson_2)
        self.assertEqual(participant_lessons[2], participant_lesson_3)
        self.assertEqual(participant_lessons[3], participant_lesson_4)
        self.assertFalse(hasattr(participant_lessons[0], "is_missed"))
        self.assertTrue(hasattr(participant_lessons[1], "is_missed"))
        self.assertFalse(hasattr(participant_lessons[2], "is_missed"))
        self.assertFalse(hasattr(participant_lessons[3], "is_missed"))

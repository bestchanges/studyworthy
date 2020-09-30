from django.apps import apps
from django.contrib.auth.models import Group, User
from django.test import TestCase

from djangoapps.lms.apps import LmsConfig
from djangoapps.lms.models.lms_models import Course, Flow, Lesson, Student, FlowLesson


class ModelsTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(title='test course')
        self.lessons = []
        for number in range(10):
            self.lessons.append(Lesson.objects.create(
                course=self.course,
                title=f'lesson {number}',
            ))
        self.user_student = User.objects.create(username='student', password='student')
        self.user_teacher = User.objects.create(username='teacher', password='teacher')

    def test_apps(self):
        self.assertEqual(LmsConfig.name, 'djangoapps.lms')
        self.assertEqual(apps.get_app_config('lms').name, 'djangoapps.lms')

    def test_flow_create(self):
        flow = Flow.objects.create(course=self.course, name='flow 1', schedule_template='Mon 18:00, Fri 18:00')
        self.assertTrue(flow.group.name, "Should have students_group")
        self.assertEqual(FlowLesson.objects.filter(flow=flow).count(), 10, "Lessons must be copied from course")
        self.assertEqual(flow.flow_lessons.count(), 10, "Lessons must be copied from course")

    def test_enroll_student_adds_to_students_group(self):
        flow = Flow.objects.create(course=self.course, name='flow 1')
        student = Student.objects.create(flow=flow, user=self.user_student)
        self.assertTrue(self.user_student.groups.filter(name=flow.group.name).exists(),
                        "Student must be included into Flows group")

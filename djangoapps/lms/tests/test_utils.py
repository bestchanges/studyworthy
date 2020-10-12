from datetime import timedelta
from unittest import TestCase

from django.utils.timezone import now

from djangoapps.lms.models import Course, Lesson, Flow, FlowLesson
from djangoapps.lms.utils import lessons_open_ready


class TestUtils(TestCase):
    def _add(self, model):
        return model
    #     if not hasattr(self, 'models'):
    #         self.models = []
    #     self.models.append(model)
    #     return model
    #
    # def tearDown(self) -> None:
    #     if not hasattr(self, 'models'):
    #         return
    #     for model in reversed(self.models):
    #         model.delete()

    def setUp(self):
        self.course = self._add(Course.objects.create(title='test course'))
        for number in range(10):
            self._add(self.course.add_lesson(Lesson.objects.create(title=f'lesson {number}')))
        # self.user_student = self._add(User.objects.create(username='student', password='student'))
        # self.user_teacher = self._add(User.objects.create(username='teacher', password='teacher'))
        self.flow = self._add(self.course.create_flow())
        # self.student = self._add(Student.objects.create(user=self.user_student, flow=self.flow))
        # self.teacher = self._add(Teacher.objects.create(user=self.user_teacher, flow=self.flow))

    def test_lessons_open_ready(self):
        assert self.flow.state != Flow.STATE_ONGOING
        assert not self.flow.flow_lessons.get(ordering=2).is_opened
        assert not self.flow.flow_lessons.get(ordering=1).is_opened
        # let's set the first flow_lesson as to be open at past
        flow_lesson: FlowLesson = self.flow.flow_lessons.get(ordering=1)
        today = now()
        yesterday = today - timedelta(days=1)
        flow_lesson.open_planned_at = yesterday
        flow_lesson.save()
        assert flow_lesson.open_planned_at < today
        lessons_open_ready()

        assert not self.flow.flow_lessons.get(ordering=1).is_opened, "For flow which is not started doesn't open the lessons"
        assert not self.flow.flow_lessons.get(ordering=2).is_opened, "Future lessons should not open"

        self.flow.state = Flow.STATE_ONGOING
        self.flow.save()
        lessons_open_ready()
        flow_lesson: FlowLesson = self.flow.flow_lessons.first()
        assert self.flow.flow_lessons.get(ordering=1).is_opened, "For flow which is started should open the lessons"
        assert not self.flow.flow_lessons.get(ordering=2).is_opened, "Future lessons should not open"

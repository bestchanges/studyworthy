import datetime
import json
import uuid
from collections import OrderedDict

from cms.utils.helpers import classproperty
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

import djangoapps.lms.questions
from djangoapps.common.enums import TextChoices
from djangoapps.common.models import OrderingMixin, CodeNaturalKeyAbstractModel, StatefulMixin, CreatedUpdatedMixin
from djangoapps.lms import questions
from djangoapps.lms.schedule import events_generator
from djangoapps.lms.signals import lesson_available, lesson_unavailable, flow_started


class Lesson(CodeNaturalKeyAbstractModel):
    class TimingType(TextChoices):
        ON_DEMAND = 'ON_DEMAND', _('в удобное время')
        ONLINE = 'ONLINE', _('в определенное время')

    title = models.CharField(max_length=250, default=_('Lesson name'), verbose_name=_('Title'))
    brief = models.TextField(max_length=5000, blank=True, null=True, help_text='Описание содержимого урока')
    timing_type = models.CharField(
        max_length=100, choices=TimingType.choices, default='ON_DEMAND',
        verbose_name=_('Вид доступа'),
        help_text=_("В какое время участник может получить доступ к материалам урока. "
                    "Попасть на вебинар может быть только в определенное время."))
    webinar = models.ForeignKey('Webinar', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')

    def __str__(self):
        return f'{self.title}'


class Unit(CodeNaturalKeyAbstractModel):
    """
    Course Unit.

    Contains several ordered Lessons.
    It's actually subcourse.
    """
    code = models.CharField(max_length=250, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=250)
    course = models.ForeignKey('Course', null=True, on_delete=models.CASCADE, related_name='units')

    class Meta:
        verbose_name = _('Unit')
        verbose_name_plural = _('Units')

    def __str__(self):
        return self.name


class CourseLesson(OrderingMixin, models.Model):
    """
    One element in Unit. Need for proper ordering.

    Used in through for ManyToMany reference
    """
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='course_lessons')
    unit = models.ForeignKey(
        Unit, blank=True, null=True, on_delete=models.CASCADE, related_name='course_lessons',
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return str(self.lesson)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.ordering:
            self.ordering = self.__class__.objects.filter(course=self.course).count() + 1
        super().save(force_insert, force_update, using, update_fields)


class Course(CodeNaturalKeyAbstractModel):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    STATE_CHOICES = [(state, state) for state in (DRAFT, ACTIVE, ARCHIVED)]

    code = models.CharField(max_length=250, unique=True, default=uuid.uuid4)
    title = models.CharField(
        max_length=250, default='',
        verbose_name=_("Название"))
    state = models.CharField(max_length=8, choices=STATE_CHOICES, default=DRAFT)
    learning_objective = models.TextField(
        max_length=4000, default='', blank=True,
        verbose_name=_('Цель обучения'),
        help_text=_('Что студент научится делать в результате прохождения курса'))

    class Meta:
        verbose_name = _('Курс')
        verbose_name_plural = _('Курсы')

    def __str__(self):
        return f'{self.title}'

    def add_lesson(self, lesson: Lesson, unit: Unit = None) -> CourseLesson:
        return CourseLesson.objects.create(
            course=self,
            lesson=lesson,
            unit=unit,
        )

    def create_flow(self) -> 'Flow':
        flow_name = '{course_code}-{number}'.format(
            course_code=self.code,
            number=Flow.objects.filter(course=self).count() + 1,
        )
        return Flow.objects.create(
            course=self,
            name=flow_name,
        )

    def lessons_by_unit(self):
        """
        Return ordered dict, where keys is units, values are list of course_lessons

        Note: that the order of units is defined by course_lesson first unit appearance
        """
        result = OrderedDict()
        for course_lesson in self.course_lessons.all():
            if not course_lesson.unit in result:
                result[course_lesson.unit] = []
            result[course_lesson.unit].append(course_lesson)
        return result


class Flow(models.Model):
    class Meta:
        verbose_name = _('Поток')
        verbose_name_plural = _('Потоки')

    STATE_DRAFT = 'draft'
    STATE_PLANNED = 'planned'
    STATE_ONGOING = 'ongoing'
    STATE_FINISHED = 'finished'
    STATE_CANCELLED = 'cancelled'

    ACTIVE_STATES = [STATE_PLANNED, STATE_ONGOING, STATE_FINISHED]

    CHOICES_STATE = [(elem, _(elem)) for elem in (
        STATE_DRAFT, STATE_PLANNED, STATE_ONGOING, STATE_FINISHED, STATE_CANCELLED
    )]

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='flows')
    name = models.CharField(max_length=200, default='')
    state = models.CharField(max_length=20, choices=CHOICES_STATE, default=STATE_PLANNED)

    schedule_template = models.CharField(max_length=200, null=True, default="Mon 15:00, Tue 15:00, Sat 19:00",
                                         help_text=_('Regular plan of learning'))

    start_planned_at = models.DateTimeField(default=now, null=True, blank=True)
    finish_planned_at = models.DateTimeField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if is_create:
            for course_lesson in self.course.course_lessons.all():
                FlowLesson.objects.create(
                    flow=self,
                    course_lesson=course_lesson,
                    lesson=course_lesson.lesson,
                    unit=course_lesson.unit,
                    ordering=course_lesson.ordering,
                )
            self.reschedule()

    def lessons_by_unit(self):
        """
        Return ordered dict, where keys is units, values are list of course_lessons

        Note: that the order of units is defined by course_lesson first unit appearance
        """
        result = OrderedDict()
        for flow_lesson in self.flow_lessons.all():
            if not flow_lesson.unit in result:
                result[flow_lesson.unit] = []
            result[flow_lesson.unit].append(flow_lesson)
        return result

    def reschedule(self):
        generator = events_generator(self.schedule_template, self.start_planned_at)
        for flow_lesson in self.flow_lessons.all():
            timestamp = next(generator)
            flow_lesson.open_planned_at = timestamp
            flow_lesson.save()

    def start_flow(self):
        if self.state not in Flow.STATE_PLANNED:
            return
        self.started_at = timezone.now()
        self.state = Flow.STATE_ONGOING
        self.save()
        flow_started.send(sender=Flow, flow=self)


class FlowLesson(OrderingMixin, models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='flow_lessons')
    # this is just for reference. All significant fields are copied from the CourseLesson
    course_lesson = models.ForeignKey(CourseLesson, null=True, on_delete=models.SET_NULL, related_name='+')
    unit = models.ForeignKey(Unit, null=True, on_delete=models.CASCADE, related_name='+')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='flow_lessons')
    flow_webinar = models.ForeignKey(
        'Webinar', null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_('Вебинар'),
        help_text=_("Вебинар урока для данного потока. Если не указан, то используется вебинар урока."))

    is_opened = models.BooleanField(default=False)
    open_planned_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.flow} {self.lesson}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create_new = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if is_create_new:
            for participant in self.flow.participants.filter(role=Student.ROLE):
                flow_lesson = self
                ParticipantLesson.objects.create(
                    participant=participant,
                    flow_lesson=flow_lesson,
                )

    @property
    def webinar(self):
        return self.flow_webinar if self.flow_webinar else self.lesson.webinar

    @webinar.setter
    def webinar(self, value):
        self.flow_webinar = value

    def open_lesson(self, by_user=None):
        if self.is_opened:
            return
        self.is_opened = True
        self.opened_at = timezone.now()
        self.save()
        lesson_available.send(sender=FlowLesson, flow_lesson=self, by_user=by_user)

    def close_lesson(self, by_user=None):
        if not self.is_opened:
            return
        self.is_opened = False
        self.save()
        lesson_unavailable.send(sender=FlowLesson, flow_lesson=self, by_user=by_user)


class Participant(models.Model):
    ROLE_TEACHER = 'TEACHER'
    ROLE_ADMIN = 'ADMIN'
    ROLE_STUDENT = 'STUDENT'

    ROLE = None  # To be overridden in children

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='participants'
    )

    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='participants')
    role = models.CharField(max_length=20,
                            choices=[(role, _(role)) for role in [ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT]])
    notes = models.CharField(max_length=200, default='', blank=True,
                             verbose_name=_('Notes'), help_text=_('Visible for stuff only'))

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        unique_together = [['flow', 'user']]

    def __init__(self, *args, **kwargs):
        self._meta.get_field('role').default = self.ROLE
        super(Participant, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create_new = self.pk is None

        super().save(force_insert, force_update, using, update_fields)

        if is_create_new and self.flow:
            for flow_lesson in self.flow.flow_lessons.all():
                ParticipantLesson.objects.create(
                    participant=self,
                    flow_lesson=flow_lesson,
                )

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f'{self.full_name}'


class Teacher(Participant):
    ROLE = Participant.ROLE_TEACHER

    class Meta:
        verbose_name = _('Teacher')
        verbose_name_plural = _('Teachers')


class Admin(Participant):
    ROLE = Participant.ROLE_ADMIN

    class Meta:
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')


class Student(Participant):
    ROLE = Participant.ROLE_STUDENT

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    def lessons_by_unit(self):
        """
        Return ordered dict, where keys is units, values are list of participant_lesson list

        Note: that the order of units is defined by course_lesson first unit appearance
        """
        result = OrderedDict()
        for participant_lesson in self.participant_lessons.all():
            unit = participant_lesson.flow_lesson.unit
            if not unit in result:
                result[unit] = []
            result[unit].append(participant_lesson)
        return result

    def list_lessons_marked_missed(self, participant_lessons=None):
        mark_as_missed = False
        result = []
        iterable = participant_lessons or self.participant_lessons.reverse()
        for participant_lesson in iterable:
            if mark_as_missed and participant_lesson.flow_lesson.is_opened and \
                    not participant_lesson.is_completed:
                participant_lesson.is_missed = True
            if participant_lesson.flow_lesson.is_opened:
                mark_as_missed = True
            result.append(participant_lesson)
        result.reverse()
        return result

    def list_lessons_marked_blocked(self, participant_lessons=None):
        mark_as_blocked = False
        result = []
        iterable = participant_lessons or self.participant_lessons.all()
        for participant_lesson in iterable:
            if participant_lesson.flow_lesson.is_opened \
                    and not participant_lesson.is_completed \
                    and mark_as_blocked:
                participant_lesson.is_blocked = True
            result.append(participant_lesson)
        return result


class ParticipantLesson(models.Model):
    RESULT_ACCEPTED = 'accepted'
    RESULT_FAILED = 'failed'
    RESULT_REJECTED = 'rejected'

    CHOICES_RESULT = (
        (RESULT_ACCEPTED, _('Accepted')),
        (RESULT_FAILED, _('Failed')),
        (RESULT_REJECTED, _('Rejected')),
    )

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='participant_lessons')
    # this is just for reference. All significant fields are copied from the FlowLesson
    flow_lesson = models.ForeignKey(FlowLesson, null=True, blank=True, on_delete=models.CASCADE, related_name='+')

    is_opened = models.BooleanField(default=False)

    when_opened = models.DateTimeField(null=True, blank=True,
                                       help_text=_('When the lesson becomes accessible for sudent'))
    when_completed = models.DateTimeField(null=True, blank=True,
                                          help_text=_('When the student has marked lesson as completed'))
    # TODO: maybe remove this field. As soon it duplicates in the Response
    when_checked = models.DateTimeField(
        null=True, blank=True,
        help_text=_('When the teacher has checked the task'))
    check_result = models.CharField(
        default=None, null=True, blank=True, choices=CHOICES_RESULT, max_length=30,
        help_text=_('Check result for last response'))
    score = models.IntegerField(
        default=None, null=True, blank=True, verbose_name=_('Score'),
        help_text=_('Score for last teacher response'))

    class Meta:
        unique_together = ['participant', 'flow_lesson']
        ordering = ['participant', 'flow_lesson']

    def __str__(self):
        return f'{self.flow_lesson} {self.participant}'

    @property
    def is_completed(self):
        return self.when_completed is not None

    @property
    def is_task_accepted(self):
        return self.check_result == self.RESULT_ACCEPTED

    @property
    def is_task_rejected(self):
        return self.check_result == self.RESULT_REJECTED

    @property
    def is_task_failed(self):
        return self.check_result == self.RESULT_FAILED

    @property
    def is_checked(self):
        return self.when_checked is not None


class Question(OrderingMixin, models.Model):
    """Вопрос для проверочного задания к уроку"""

    TYPES_CHOICES = [(name, type.label) for name, type in questions.ALL_TYPES.items()]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='questions',
        help_text=_('Урок к которому относится'))
    code = models.SlugField(
        max_length=100,
        verbose_name=_('Код'),
        help_text=_('Уникален среди вопросов этого урока'))
    name = models.CharField(
        max_length=200,
        verbose_name=_('Вопрос'),
    )
    text = models.TextField(
        max_length=3000, null=True, blank=True,
        verbose_name=_('Текст вопроса'),
    )
    type = models.CharField(
        max_length=100, choices=TYPES_CHOICES, blank=True, null=True,
        verbose_name=_("Тип ответа"),
    )
    choices = models.TextField(
        max_length=1000, blank=True, null=True,
        verbose_name=_('Варианты ответа'),
        help_text=_('Возможные значения (если применимо)'),
    )
    required = models.BooleanField(default=False)
    score = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Оценка'),
        help_text=_('Оценка за правильный ответ на вопрос'),
    )

    # autocheck feature
    is_autocheck = models.BooleanField(
        default=False,
        verbose_name=_('Авто проверка?'),
        help_text=_('Если "Да", то должно быть заполнено поле "Правильный ответ"'))
    correct_answer = models.TextField(
        max_length=20000, null=True, blank=True,
        verbose_name=_('Правильный ответ(ы)'),
        help_text=_('Значение правильного ответа. В нескольких значений - каждое значение на отдельной строке'))

    def autocheck_answer(self, answer: str):
        """
        Check the responce automatically.
        Raises ValueError if answer is None.
        Raises ValueError if autocheck is disabled.

        :return earned score
        """
        if answer is None:
            raise ValueError('no answer given')
        if not self.is_autocheck:
            raise ValueError('auctocheck disabled')
        score = 0
        if answer == self.correct_answer:
            score = self.score
        return score


class LessonResponse(StatefulMixin, CreatedUpdatedMixin, models.Model):
    """Student response to he lesson and check."""

    class State(TextChoices):
        FILLED = 'FILLED', _('Filled')
        CHECKED = 'CHECKED', _('Checked')

    # student's flow_lesson. (Using more generic ParticipantLesson but it's mostly for Students)
    participant_lesson = models.ForeignKey(ParticipantLesson, on_delete=models.CASCADE, related_name='answer')

    # student's part
    answers_json = models.TextField(
        max_length=2000,
        help_text=_('JSON answers of the student on questions of the lesson'))
    when_sent_by_student = models.DateTimeField(
        null=True, blank=True,
        help_text=_('When the student send this response'))

    # teacher's part
    assigned_to = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='+',
        null=True, blank=True,
        help_text=_('The teacher who is to check this response'))
    when_checked_by_teacher = models.DateTimeField(
        null=True, blank=True,
        help_text=_('When the teacher check this response'))

    # this fields to be filled during assessment
    comments_json = models.TextField(
        max_length=10000,
        help_text=_('JSON comments on student\'s answers. Structure: question_code: answer text'))
    check_comment = models.TextField(
        null=True, blank=True,
        help_text=_('Comment on this whole response. Structure: question_code: {"score": value, "comment": value}')
    )
    is_accepted = models.BooleanField(
        null=True, blank=True,
        help_text=_('Is student\'s response accepted'))
    score = models.IntegerField(
        null=True, blank=True,
        help_text=_('Overall score for this response'))

    def autockeck(self):
        """Performs autocheck for questions which support autocheck."""
        answers = json.loads(self.answers_json) if self.answers_json else {}
        questions = {q.code: q for q in self.participant_lesson.flow_lesson.lesson.questions.all()}
        comments = json.loads(self.answers_json) if self.answers_json else {}

        overall_score = 0
        for question_code, answer in answers.items():
            question: Question = questions[question_code]
            assert question, f'No question with code {question_code}. Codes: {questions.keys()}'
            if question.is_autocheck:
                score = question.autocheck_answer(answer)
                overall_score += score
                comments[question_code] = {'score': score, 'comment': ''}

        self.comments_json = json.dumps(comments, indent=4)
        self.score = overall_score
        self.save()


class Webinar(CodeNaturalKeyAbstractModel, StatefulMixin, models.Model):

    class State(TextChoices):
        DRAFT = 'DRAFT'
        PLANNED = 'PLANNED'
        ONGOING = 'ONGOING'
        FINISHED = 'FINISHED'
        CANCELLED = 'CANCELLED'

    class Platform(TextChoices):
        YOUTUBE = 'youtube'
        SKYPE = 'skype'
        ZOOM = 'zoom'
        OTHER = 'other'

    name = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Название вебинара'))
    state = models.CharField(max_length=100, choices=State.choices, default='DRAFT', verbose_name=_('Состояние'))

    start_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Начало в'))
    duration = models.DurationField(null=True, blank=True, verbose_name='Продолжительность ЧЧ:ММ')

    platform = models.CharField(
        choices=Platform.choices, max_length=100, null=True, blank=True, verbose_name=_('Платформа вебинаров'))
    platform_id = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name=_('ID вебинара на платформе'),
        help_text=_("Может быть номер, строка-код или ссылка"))

    class Meta:
        verbose_name = _("Вебинар")
        verbose_name_plural = _("Вебинары")

    def __str__(self):
        return self.name

    @property
    def finish_at(self):
        """Get finish timestamp"""
        return self.start_at + self.duration

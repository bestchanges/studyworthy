import uuid
from collections import OrderedDict

import cms.api
from cms.models import PlaceholderField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from djangoapps.erp.models import CodeNaturalKeyAbstractModel
from djangoapps.lms.schedule import events_generator
from djangoapps.lms.signals import lesson_available, lesson_unavailable, flow_started


class Lesson(CodeNaturalKeyAbstractModel):
    title = models.CharField(max_length=250, default=_('Lesson name'), verbose_name=_('Title'))
    code = models.CharField(
        max_length=250, unique=True, default=uuid.uuid4, verbose_name=_('Code'))
    lesson_content = PlaceholderField('lesson_content', related_name='lesson_content')
    support_content = PlaceholderField('support_content', related_name='support_content')
    show_common_content = models.BooleanField(
        default=True,
        help_text=_('Display content common for all lessons across course at the bottom of lesson content'))

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')

    def __str__(self):
        return f'{self.title}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # TODO: fill from last created lesson
        # cms.api.add_plugin(
        #     plugin_type='TextCMSPlugin',
        #     placeholder=self.lesson_content,
        #     language='ru',
        #     body="Sample text"
        # )


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


class CourseLesson(models.Model):
    """
    One element in Unit. Need for proper ordering.

    Used in through for ManyToMany reference
    """
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='course_lessons')
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.CASCADE, related_name='course_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name='+')
    ordering = models.PositiveIntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.ordering:
            self.ordering = self.__class__.objects.filter(course=self.course).count() + 1
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['ordering']


class Course(CodeNaturalKeyAbstractModel):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'
    STATE_CHOICES = [(state, state) for state in (DRAFT, ACTIVE, ARCHIVED)]

    code = models.CharField(max_length=250, unique=True, default=uuid.uuid4)
    title = models.CharField(max_length=250, default=_('Course name'))
    state = models.CharField(max_length=8, choices=STATE_CHOICES, default=DRAFT)
    icon = models.CharField(max_length=100, default='fas fa-graduation-cap')
    flow_content = PlaceholderField('flow_content', related_name='flow_content',
                                    help_text=_('Content shown on the flow index page'))
    common_content = PlaceholderField('lesson_common_content', related_name='lesson_common_content',
                                      help_text=_('Content shown in each course lesson'))

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

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def __str__(self):
        return f'{self.title}'


# TODO: make flow - Document
class Flow(models.Model):
    class Meta:
        verbose_name = _('Flow')
        verbose_name_plural = _('Flows')

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


class FlowLesson(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, related_name='flow_lessons')
    # this is just for reference. All significant fields are copied from the CourseLesson
    course_lesson = models.ForeignKey(CourseLesson, null=True, on_delete=models.SET_NULL, related_name='+')
    unit = models.ForeignKey(Unit, null=True, on_delete=models.CASCADE, related_name='+')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='flow_lessons')
    ordering = models.PositiveIntegerField(default=0, help_text="Ordering number")

    is_opened = models.BooleanField(default=False)
    open_planned_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['ordering']

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
    when_checked = models.DateTimeField(null=True, blank=True, help_text=_('When the teacher has checked the task'))
    check_result = models.CharField(
        default=None, null=True, blank=True, choices=CHOICES_RESULT, max_length=30, verbose_name=_('Check result'))
    score = models.IntegerField(
        default=None, null=True, blank=True, verbose_name=_('Score'), help_text=_('Score for student response'))

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

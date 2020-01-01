"""
Learning process related models.
"""

from django.conf import settings
from django.db import models

from study import config
from study.models.base import CodeNaturalKeyAbstractModel, Person
from study.models.content import Course, Unit


class Learning(CodeNaturalKeyAbstractModel):

    class Meta:
        verbose_name = 'learning'
        verbose_name_plural = 'learnings'

    class State(models.TextChoices):
        DRAFT = 'draft'
        PLANNED = 'planned'
        ONGOING = 'ongoing'
        FINISHED = 'finished',
        CANCELLED = 'cancelled'

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    state = models.CharField(max_length=20, choices=State.choices, default=State.PLANNED)
    schedule = models.CharField(max_length=200, null=True, help_text='Regular plan of learning of units. Example: "Mon 15:00, Tue 15:00, Sat 19:00"')
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in config.TIMEZONES], default=settings.TIME_ZONE)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    start_planned_at = models.DateTimeField(null=True, blank=True)
    finish_planned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # TODO: def timetable()

    def __str__(self):
        return f'Learning {self.code}'


class Participant(models.Model):
    class Role(models.TextChoices):
        STUDENT = 'student'
        TEACHER = 'teacher'
        ADMIN = 'admin',

    class State(models.TextChoices):
        CANDIDATE = 'candidate'
        ACTIVE = 'active'
        CANCELLED = 'cancelled',

    class Meta:
        unique_together = [['learning', 'person', 'role']]

    learning = models.ForeignKey(Learning, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices)
    state = models.CharField(max_length=20, choices=State.choices)
    code_repository = models.CharField(max_length=255, default='', blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    assigned_at = models.DateTimeField(auto_now_add=True, editable=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.role} {self.person.get_full_name()}'


class Lesson(models.Model):
    class Meta:
        unique_together = [['unit', 'learning']]

    class State(models.TextChoices):
        HIDDEN = "hidden"
        CLOSED = "closed"
        OPENED = "opened"
        FINISHED = "finished"
        CANCELLED = "cancelled"

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    learning = models.ForeignKey(Learning, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=State.choices)
    order = models.IntegerField()
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(null=True, blank=True)
    open_planned_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Lesson: {self.unit} for {self.learning}'


class Presence(models.Model):
    """
    Represents state of processing of the Lesson by the Student. Unique for combination of unit and student.
    """

    class Meta:
        unique_together = [['lesson', 'student'], ]

    student = models.ForeignKey(Participant, limit_choices_to={'role': 'student'}, related_name='+', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.lesson} {self.student}: [{"X" if self.completed else " "}]'


class Decision(models.Model):

    class State(models.TextChoices):
        NONE = "none", "None"
        DONE = "done", "Done"
        WAIT_REVIEW = "wait_review", "To review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    presence = models.ForeignKey(Presence, on_delete=models.CASCADE)
    value_float = models.FloatField(null=True)
    value_string = models.CharField(max_length=255, null=True)
    value_text = models.TextField(null=True)
    value_link = models.URLField(null=True)
    comment = models.TextField(default='')
    state = models.CharField(max_length=20, choices=State.choices, default=State.NONE)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    assigned_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)


class Review(models.Model):
    decision = models.OneToOneField(Decision, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        Participant, null=True, limit_choices_to={'role': 'teacher'},
        related_name='+', on_delete=models.CASCADE,
    )
    score = models.IntegerField(null=True)
    reviewer_comment = models.TextField(default='')

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    assigned_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)




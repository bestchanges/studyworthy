from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from study import config


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


class Category(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING)


class ByCodeManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class CodeNaturalKeyAbstractModel(models.Model):
    code = models.CharField(max_length=36, unique=True)

    objects = ByCodeManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.code,)


class Person(CodeNaturalKeyAbstractModel):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(null=True, unique=True)  # TODO: can we use unique=True for nullable ?
    phone = models.CharField(max_length=20, default='', blank=True)
    skype = models.CharField(max_length=100, default='', blank=True)
    google_account = models.CharField(max_length=200, default='', blank=True)
    github_account = models.CharField(max_length=200, default='', blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default='ru')
    country = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in config.TIMEZONES], default=settings.TIME_ZONE)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.get_full_name()} {self.email}'


class UserPerson(AbstractUser):
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)


@receiver(post_save, sender=UserPerson)
def on_user_create(sender, instance: UserPerson, created, **kwargs):
    if created:
        person = Person.objects.create(
            first_name=instance.first_name, last_name=instance.last_name,
            email=instance.email, code=instance.username
        )
        instance.person = person


class Author(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Author: {self.person.get_full_name()}'


class Course(CodeNaturalKeyAbstractModel):
    class State(models.TextChoices):
        DRAFT = 'draft'
        ACTIVE = 'active'
        ARCHIVED = 'archived',

    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)
    short_description = models.CharField(max_length=500, default='')
    long_description = models.TextField(default='')
    content_repository = models.CharField(max_length=255, help_text="GIT repository with course content")
    students_template_repository = models.CharField(max_length=255, help_text="Template GIT repository for students submissions")

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    activated_at = models.DateTimeField(null=True)
    archived_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.title}'


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
        return f'{self.code}'


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


class Section(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['course', 'order'], ]

    title = models.CharField(max_length=200)
    order = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} ({self.code})'


class Unit(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['course', 'section', 'order'], ['course', 'slug']]

    class ContentType(models.TextChoices):
        TEXT = "text"
        LINK = "link"
        VIDEO = "video"
        AUDIO = "audio"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50)
    section = models.ForeignKey(Section, null=True, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField()
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.TEXT)
    content = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Task(models.Model):
    class Type(models.TextChoices):
        QUIZ = "quiz"
        TEXT = "text"

    class DecisionType(models.TextChoices):
        NUMBER = "number"
        TEXT = "text"
        LINK = "link"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TEXT)
    description = models.TextField(default='')

    decision_type = models.CharField(max_length=20, choices=DecisionType.choices)
    decision_deadline_days = models.IntegerField(null=True)

    max_score = models.IntegerField(null=True)
    pass_score = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


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


class ApplicationForm(models.Model):
    learning = models.ForeignKey(Learning, on_delete=models.PROTECT, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    comment = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


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
    code = models.SlugField(unique=True)

    objects = ByCodeManager()

    class Meta:
        abstract = True

    def natural_key(self):
        return (self.code,)


class Person(CodeNaturalKeyAbstractModel):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)
    skype = models.CharField(max_length=100, default='', blank=True)
    google_account = models.CharField(max_length=200, default='', blank=True)
    github_account = models.CharField(max_length=200, default='', blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGES, default='ru')
    country = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)

    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(default=timezone.now)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.get_full_name()} {self.email}'


@receiver(post_save, sender=User)
def on_user_create(sender, instance: User, created, **kwargs):
    if created:
        Person.objects.create(
            user=instance,
            first_name=instance.first_name, last_name=instance.last_name,
            email=instance.email, code=instance.username
        )


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

    def __str__(self):
        return f'{self.title}'


class Learning(CodeNaturalKeyAbstractModel):

    class Meta:
        verbose_name = 'learning'
        verbose_name_plural = 'learnings'

    class State(models.TextChoices):
        PLANNED = 'planned'
        IN_PROGRESS = 'in_progress'
        FINISHED = 'finished',
        CANCELLED = 'cancelled'

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    state = models.CharField(max_length=20, choices=State.choices, default=State.PLANNED)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    start_planned_at = models.DateTimeField(null=True, blank=True)
    finish_planned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

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
    admin_notes = models.TextField(default='', blank=True)

    assigned_at = models.DateTimeField(auto_now_add=True, editable=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.role} {self.person.get_full_name()}'


class Section(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['learning', 'order'], ]

    title = models.CharField(max_length=200)
    order = models.IntegerField()
    learning = models.ForeignKey(Learning, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} ({self.code})'


class Unit(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['section', 'order'], ]

    class TaskType(models.TextChoices):
        NONE = "none"
        SELF_CHECK = "self_check"
        ASSIGNMENT = "assignment"

    class State(models.TextChoices):
        HIDDEN = "hidden"
        WAITING = "waiting"
        OPENED = "opened"
        FINISHED = "finished"

    title = models.CharField(max_length=200)
    order = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.NONE)
    task_details = models.TextField(default='')
    submission_timespan_days = models.IntegerField(default=0)
    pass_score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title} ({self.code})'


class CheckMark(models.Model):
    """
    Represents state of processing of the Unit by the Student. Unique for combination of unit and student.
    """

    class Meta:
        unique_together = [['unit', 'student'], ]

    class State(models.TextChoices):
        EMPTY = "empty"
        CHECKED = "checked"

    student = models.ForeignKey(Participant, limit_choices_to={'role': 'student'}, related_name='+', on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    score = models.IntegerField(null=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.EMPTY)

    checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.unit} {self.student.person.get_full_name()}: {self.state}'


class Submission(models.Model):

    class State(models.TextChoices):
        NONE = "none", "None"
        DONE = "done", "Done"
        WAIT_REVIEW = "wait_review", "To review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    check_mark = models.ForeignKey(CheckMark, on_delete=models.CASCADE)
    text = models.TextField(default='')
    student_comment = models.TextField(default='')
    reviewer = models.ForeignKey(
        Participant, null=True, limit_choices_to={'role': 'teacher'},
        related_name='+', on_delete=models.CASCADE,
    )
    score = models.IntegerField(null=True)
    reviewer_comment = models.TextField(default='')
    state = models.CharField(max_length=20, choices=State.choices, default=State.NONE)
    can_student_resubmit = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    assigned_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    resubmitted_at = models.DateTimeField(null=True, blank=True)


class ApplicationForm(models.Model):
    learning = models.ForeignKey(Learning, on_delete=models.PROTECT, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    comment = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

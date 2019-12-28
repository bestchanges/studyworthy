from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


class Category(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING)


class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('en', 'English'),
        ('ua', 'Ukrainian')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    skype = models.CharField(max_length=100, default='', blank=True)
    google_account = models.CharField(max_length=100, default='', blank=True)
    github_account = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=20, default='', blank=True)

    def __str__(self):
        return f'Profile for {self.user.get_full_name()} {self.user.username} '


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        Token.objects.create(user=instance)


class Author(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Author: {self.user_profile.user.username} {self.user_profile.user.get_full_name()}'


class Course(models.Model):
    class State(models.TextChoices):
        DRAFT = 'draft'
        ACTIVE = 'active'
        ARCHIVED = 'archived',

    title = models.CharField(max_length=200)
    code = models.SlugField(unique=True)
    authors = models.ManyToManyField(Author)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)
    short_description = models.CharField(max_length=500, default='')
    long_description = models.TextField(default='')
    content_repository = models.CharField(max_length=255, help_text="GIT repository with course content")
    students_template_repository = models.CharField(max_length=255, help_text="Template GIT repository for students submissions")

    def __str__(self):
        return f'{self.title}'


class CourseFlow(models.Model):
    class Meta:
        unique_together = [['course', 'code']]

    class State(models.TextChoices):
        PLANNED = 'planned'
        IN_PROGRESS = 'in_progress'
        FINISHED = 'finished',
        CANCELLED = 'cancelled'

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    code = models.SlugField(unique=True, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.PLANNED)

    created_at = models.DateField(auto_now_add=True, editable=False)
    start_planned_at = models.DateField(null=True, blank=True)
    finish_planned_at = models.DateField(null=True, blank=True)
    started_at = models.DateField(null=True, blank=True)
    finished_at = models.DateField(null=True, blank=True)
    cancelled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.code}'


class Participant(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('expert', 'Expert'),
        ('admin', 'Admin')
    ]

    class Meta:
        unique_together = [['flow', 'user_profile', 'role']]

    flow = models.ForeignKey(CourseFlow, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    code_repository = models.CharField(max_length=255, default='', blank=True)
    student_score = models.IntegerField(blank=True, null=True)
    assigned_at = models.DateField(auto_now_add=True, editable=False)
    deactivated_at = models.DateField(null=True, blank=True)

    @property
    def nickname(self):
        return "%s_%s" % (self.user_profile.user.username)


class FlowSection(models.Model):
    class Meta:
        unique_together = [['flow', 'code'], ['flow', 'order'], ]

    title = models.CharField(max_length=200)
    code = models.SlugField(max_length=20)
    order = models.IntegerField()
    flow = models.ForeignKey(CourseFlow, on_delete=models.CASCADE)


class FlowUnit(models.Model):
    class Meta:
        unique_together = [['section', 'code'], ['section', 'order'], ]

    class TaskType(models.TextChoices):
        NONE = "none", "None"
        SELF_CHECK = "self_check", "Self check"
        ASSIGNMENT = "assignment", "Assignment"

    class State(models.TextChoices):
        HIDDEN = "hidden"
        WAITING = "waiting"
        OPENED = "opened"
        FINISHED = "finished"

    title = models.CharField(max_length=200)
    code = models.SlugField(max_length=20)
    order = models.IntegerField()
    section = models.ForeignKey(FlowSection, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.NONE)
    submission_timespan_days = models.IntegerField(default=0)
    pass_score = models.IntegerField(default=0)


class StudentSubmission(models.Model):
    class Status(models.TextChoices):
        NONE = "none", "None"
        DONE = "done", "Done"
        WAIT_REVIEW = "wait_review", "To review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey(Participant, limit_choices_to={'role': 'student'}, related_name='+', on_delete=models.CASCADE)
    unit = models.ForeignKey(FlowUnit, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Participant, limit_choices_to={'role': 'teacher'}, related_name='+', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NONE)
    can_student_resubmit = models.BooleanField(default=True)
    students_comment = models.TextField(default='')
    reviewer_comment = models.TextField(default='')
    score = models.IntegerField(default=0)

    created_at = models.DateField(auto_now_add=True, editable=False)
    assigned_at = models.DateField(null=True, blank=True)
    checked_at = models.DateField(null=True, blank=True)
    resubmitted_at = models.DateField(null=True, blank=True)


class ApplicationForm(models.Model):
    flow = models.ForeignKey(CourseFlow, on_delete=models.PROTECT)
    comment = models.TextField()
    user_profile = models.ForeignKey(UserProfile, on_delete=models.PROTECT)

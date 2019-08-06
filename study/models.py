from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from slugify import slugify

class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()

class Category(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING)


class UserProfile(User):
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('en', 'English'),
        ('ua', 'Ukrainian')
    ]
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    skype = models.CharField(max_length=100)
    google_account = models.CharField(max_length=100)
    github_account = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f'Profile for {self.get_full_name()} {self.username} '


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Author(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Author: {self.user_profile.first_name} {self.user_profile.last_name}'


class Course(models.Model):
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    )

    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author)
    state = models.CharField(max_length=8, choices=STATE_CHOICES, default='draft')
    short_description = models.CharField(max_length=500, default='')
    long_description = models.TextField(default='')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Course, self).save(*args, **kwargs)


class Section(models.Model):
    name = models.CharField(max_length=200)
    order = models.IntegerField
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Unit(models.Model):
    number = models.CharField(max_length=200)
    order = models.IntegerField
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)


class CourseSession(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled')
    ]

    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    started_at = models.DateField()
    status = models.CharField(max_length=11, choices=STATUS_CHOICES)


class Participant(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('expert', 'Expert'),
        ('admin', 'Admin')
    ]
    STATUS_CHOICES = [
        ('possible', 'Possible'),
        ('active', 'Active'),
        ('lost', 'Lost')
    ]

    class Meta:
        unique_together = [['course_session', 'user_profile', 'role']]

    course_session = models.OneToOneField(CourseSession, on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    score = models.IntegerField()

    @property
    def nickname(self):
        return "%s_%s" % (self.user.first_name, self.user.last_name)


class ApplicationForm(models.Model):
    course_session = models.ForeignKey(CourseSession, on_delete=models.CASCADE)
    comment = models.TextField()
    user_profile = models.OneToOneField(UserProfile, on_delete=models.PROTECT)

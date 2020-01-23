"""
Study content related Models.
"""
import uuid

from django.db import models
from natural_keys import NaturalKeyModel

from lms.models.base import CodeNaturalKeyAbstractModel, Author


class Course(NaturalKeyModel):
    class State(models.TextChoices):
        DRAFT = 'draft'
        ACTIVE = 'active'
        ARCHIVED = 'archived',

    title = models.CharField(max_length=200)
    code = models.SlugField(max_length=70, unique=True, default=uuid.uuid4)
    authors = models.ManyToManyField(Author, blank=True)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)
    short_description = models.CharField(max_length=500, default='')
    long_description = models.TextField(default='')
    notes = models.CharField(max_length=200, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    activated_at = models.DateTimeField(null=True)
    archived_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.code} ({self.title})'


class Section(NaturalKeyModel):
    name = models.CharField(max_length=200)
    code = models.SlugField(max_length=50, default=uuid.uuid4)
    order = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = [['course', 'code'], ]

    def __str__(self):
        return f'{self.name}'


class Content(NaturalKeyModel):
    class ContentType(models.TextChoices):
        TEXT = "text/plain"
        HTML = "text/html"
        MARKDOWN = "text/markdown"
        LINK = "link/uri"
        VIDEO = "video/youtube"

    code = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.HTML)
    text = models.TextField(blank=True, null=True)
    # data = models.JSONField(blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.code} ({self.name})'


class Unit(NaturalKeyModel):
    code = models.SlugField(max_length=50, help_text="Short code to easily identify this unit across the Course", default=uuid.uuid4)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    section = models.ForeignKey(Section, null=True, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(help_text="Ordering number among the course")
    notes = models.CharField(max_length=200, null=True, blank=True)
    contents = models.ManyToManyField(Content, through='UnitContent')

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    class Meta:
        unique_together = [['course', 'code']]
        ordering = ['course', 'order', 'code']

    def __str__(self):
        return f'{self.code} ({self.name})'


class UnitContent(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    order = models.IntegerField()
    class Meta:
        ordering = ['order', 'unit', 'content']


# TODO: Actually kind of content. Proxy model for Content!
class Task(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['unit', 'order'], ]

    class Type(models.TextChoices):
        QUIZ = "quiz"
        TEXT = "text"

    class DecisionType(models.TextChoices):
        NUMBER = "number"
        TEXT = "text"
        LINK = "link"

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TEXT)
    description = models.TextField(null=True, blank=True)

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    order = models.IntegerField()

    decision_type = models.CharField(max_length=20, choices=DecisionType.choices)
    decision_deadline_days = models.IntegerField(null=True, blank=True)

    max_score = models.IntegerField(default=0)
    pass_score = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

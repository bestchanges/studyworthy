"""
Study content related Models.
"""

from django.db import models

from study.models.base import CodeNaturalKeyAbstractModel, Author


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
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)
    activated_at = models.DateTimeField(null=True)
    archived_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'Course: {self.title} {self.code}'


class Section(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['course', 'order'], ]

    name = models.CharField(max_length=200)
    order = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(null=True)

    def __str__(self):
        return f'Section {self.name} ({self.code})'


class Unit(CodeNaturalKeyAbstractModel):
    class Meta:
        unique_together = [['course', 'section', 'order'], ['course', 'slug']]

    class ContentType(models.TextChoices):
        TEXT = "text"
        LINK = "link"
        VIDEO = "video"
        AUDIO = "audio"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, help_text="Short code to easily identify this unit across the Course")

    section = models.ForeignKey(Section, null=True, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField()

    description = models.TextField(null=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.TEXT)
    content = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def __str__(self):
        return f'Unit {self.name} ({self.code})'


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



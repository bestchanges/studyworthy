from django.db import models
from slugify import slugify

class Category(models.Model):
    name = models.CharField(max_length=200)
    parentId = models.ForeignKey("self", on_delete=models.DO_NOTHING)

class User(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    language = models.CharField(max_length=200)
    skype = models.CharField(max_length=200)
    google_account = models.CharField(max_length=200)
    github_account = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)


class Author(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField


class Course(models.Model):
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived')
    )

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=8,
        choices=STATE_CHOICES,
        default='draft',
    )
    short_description = models.CharField(max_length=200)
    long_description = models.TextField
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


from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User

from study.models.base import UserPerson, Person
from study.models.content import Section, Course, Unit
from study.models.learning import Participant, Learning, Lesson

admin.site.register(User, UserPerson)


@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    pass


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


class UnitsInline(admin.TabularInline):
    fields = ['order', 'name', 'slug', 'code', 'section']
    model = Unit
    extra = 0


@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('title', 'code', 'state')
    list_filter = ['state']
    search_fields = ['title', 'code']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Properties', {
            'fields': ('code', 'state')
        }),
        ('Course Description', {
            'fields': ('title', 'short_description', 'long_description')
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('notes', 'authors'),
        }),
        ('Datetime', {
            'fields': (('created_at', 'updated_at'),),
        }),
    )
    inlines = [SectionInline, UnitsInline]


class ParticipantInline(admin.StackedInline):
    model = Participant


@admin.register(Participant)
class AdminParticipant(admin.ModelAdmin):
    list_display = ('person', 'learning', 'role')
    list_filter = ['learning']
    search_fields = ['learning']


@admin.register(Unit)
class AdminUnit(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'course',
        'section',
        'code',
    )
    list_filter = ['course']
    search_fields = ['section', 'code', 'name', 'slug']


class LessonsInline(admin.TabularInline):
    fields = ['unit', 'state', 'order', 'notes', 'open_planned_at', 'opened_at', 'finished_at', 'cancelled_at']
    readonly_fields = ['opened_at', 'finished_at', 'cancelled_at']
    model = Lesson
    extra = 0


@admin.register(Learning)
class Adminlearning(admin.ModelAdmin):
    list_display = ('course', 'code', 'state', 'started_at')
    list_filter = ['state']
    readonly_fields = ['started_at', 'finished_at', 'cancelled_at', 'created_at', 'updated_at']
    search_fields = ('code', 'course')
    fieldsets = (
        ('Properties', {
            'fields': ('code', 'course', 'state')
        }),
        ('Schedule', {
            'fields': (('start_planned_at', 'finish_planned_at'), ('schedule', 'timezone'))
        }),
        ('Additional options', {
            'classes': ('collapse',),
            'fields': ('notes',),
        }),
        ('Datetime', {
            'fields': (('started_at', 'finished_at', 'cancelled_at'), ('created_at', 'updated_at'),),
        }),
    )
    inlines = [LessonsInline]

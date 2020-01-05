from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy

from lms.models.base import Person
from lms.models.content import Section, Course, Unit
from lms.models.learning import Participant, Learning, Lesson


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


class ParticipantsInline(admin.TabularInline):
    fields = ['person', 'role', 'state', 'notes', 'created_at', 'activated_at']
    readonly_fields = ['created_at', 'activated_at']
    model = Participant
    extra = 0


def reschedule_selected(modeladmin, request, queryset):
    for learning in queryset:
        learning.reschedule()

reschedule_selected.allowed_permissions = ('delete',)
reschedule_selected.short_description = gettext_lazy("Reschedule")

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
            'classes': ('collapse',),
            'fields': (('started_at', 'finished_at', 'cancelled_at'), ('created_at', 'updated_at'),),
        }),
    )
    inlines = [ParticipantsInline, LessonsInline]
    actions = [reschedule_selected]

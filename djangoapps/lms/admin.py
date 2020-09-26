from django.contrib import admin
from django.utils.translation import gettext_lazy

from djangoapps.lms.models.base import Person, Author
from djangoapps.lms.models.content import Section, Course, Unit, Content, UnitContent, Form, Question
from djangoapps.lms.models.learning import RoleStudent, RoleTeacher, Learning, Lesson


@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    pass


@admin.register(Author)
class AdminAuthor(admin.ModelAdmin):
    search_fields = ('person__first_name', 'person__last_name', )


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


class UnitsInline(admin.TabularInline):
    fields = ['order', 'name', 'code', 'section']
    model = Unit
    show_change_link = True
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
            #'classes': ('collapse',),
            'fields': ('notes', 'authors'),
        }),
        ('Datetime', {
            'fields': (('created_at', 'updated_at'),),
        }),
    )
    autocomplete_fields = ('authors', )
    # filter_horizontal = ('authors', )
    inlines = [UnitsInline, SectionInline]


class StudentsInline(admin.TabularInline):
    fields = ['person', 'state', 'notes', 'created_at', 'activated_at']
    readonly_fields = ['created_at', 'activated_at']
    model = RoleStudent
    extra = 1


class TeachersInline(admin.TabularInline):
    fields = ['person', 'notes', 'created_at', ]
    readonly_fields = ['created_at', ]
    model = RoleTeacher
    extra = 1


@admin.register(Content)
class AdminContent(admin.ModelAdmin):
    search_fields = ('code', 'name')


class FormQuestionsInline(admin.TabularInline):
    fields = ['code', 'name', 'choices', 'correct_choices', 'score']
    model = Question
    extra = 3


@admin.register(Form)
class AdminForm(admin.ModelAdmin):
    fields = ('code', 'name', 'type', 'text', 'notes', 'decision_deadline_days', 'pass_score')
    search_fields = ('code', 'name')
    inlines = [FormQuestionsInline]


class ContentInline(admin.StackedInline):
    model = Unit.contents.through
    autocomplete_fields = ('content',)
    extra = 0


@admin.register(Unit)
class AdminUnit(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'course',
        'section'
    )
    fields = (
        'course',
        'section',
        'code',
        'order',
        'name',
        'description',
        'notes',
    )
    list_filter = ['course']
    search_fields = ['section', 'code', 'name']
    inlines = [ContentInline]


class LessonsInline(admin.TabularInline):
    fields = ['unit', 'state', 'order', 'notes', 'open_planned_at', 'opened_at', 'finished_at', 'cancelled_at']
    readonly_fields = ['opened_at', 'finished_at', 'cancelled_at']
    model = Lesson
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
            'fields': ('code', 'course', 'state', 'admin')
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
    inlines = [StudentsInline, TeachersInline, LessonsInline]
    actions = [reschedule_selected]

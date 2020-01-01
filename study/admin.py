from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User

from study.models.base import UserPerson, Person
from study.models.content import Section, Course, Unit
from study.models.learning import Participant, Learning

admin.site.register(User, UserPerson)


@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    pass


class SectionInline(admin.TabularInline):
    model = Section


@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('title', 'state')
    list_filter = ['state']
    search_fields = ['title', 'code']
    inlines = [SectionInline]


class ParticipantInline(admin.StackedInline):
    model = Participant


@admin.register(Participant)
class AdminParticipant(admin.ModelAdmin):
    list_display = ('person', 'learning', 'role')
    list_filter = ['learning']
    search_fields = ['learning']


@admin.register(Unit)
class AdminUnit(admin.ModelAdmin):
    list_display = ('section', 'course', 'code', 'name')
    list_filter = ['section']
    search_fields = ['section']


@admin.register(Learning)
class Adminlearning(admin.ModelAdmin):
    list_display = ('course', 'code', 'state', 'started_at')
    # fields = (('course', 'state'), 'started_at', 'start_planned_at')
    list_filter = ['state']
    readonly_fields = ['started_at']
    search_fields = ['code']

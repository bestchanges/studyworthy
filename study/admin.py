from django.contrib import admin

# Register your models here.
from .models import Course, Person, Author, Learning, Participant, Section, Unit


@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    pass


@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('title', 'state')
    list_filter = ['state']
    search_fields = ['title', 'code']


class ParticipantInline(admin.StackedInline):
    model = Participant


class SectionInline(admin.TabularInline):
    model = Section


@admin.register(Participant)
class AdminParticipant(admin.ModelAdmin):
    list_display = ('person', 'learning', 'role')
    list_filter = ['learning']
    search_fields = ['learning']


@admin.register(Unit)
class AdminlearningUnit(admin.ModelAdmin):
    list_display = ('section', 'code', 'title')
    list_filter = ['section']
    search_fields = ['section']


@admin.register(Learning)
class Adminlearning(admin.ModelAdmin):
    list_display = ('course', 'code', 'state', 'started_at')
    # fields = (('course', 'state'), 'started_at', 'start_planned_at')
    list_filter = ['state']
    readonly_fields = ['started_at']
    search_fields = ['code']
    inlines = [SectionInline]

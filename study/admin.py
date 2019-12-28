from django.contrib import admin

# Register your models here.
from .models import Course, UserProfile, Author, CourseFlow, Participant, FlowSection


@admin.register(UserProfile)
class AdminUserProfile(admin.ModelAdmin):
    pass


@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('title', 'state')
    list_filter = ['state']
    search_fields = ['title', 'code']


class ParticipantInline(admin.StackedInline):
    model = Participant


class SectionInline(admin.StackedInline):
    model = FlowSection


@admin.register(Participant)
class AdminParticipant(admin.ModelAdmin):
    list_display = ('flow', 'role')
    list_filter = ['flow']
    search_fields = ['flow']


@admin.register(CourseFlow)
class AdminFlow(admin.ModelAdmin):
    list_display = ('course', 'code', 'state', 'started_at')
    # fields = (('course', 'state'), 'started_at', 'start_planned_at')
    list_filter = ['state']
    readonly_fields = ['started_at']
    search_fields = ['code']
    inlines = [ParticipantInline, SectionInline]

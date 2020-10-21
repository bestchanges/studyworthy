from adminsortable2.admin import SortableInlineAdminMixin
from ckeditor.widgets import CKEditorWidget
from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from djangoapps.lms.models import Flow, Student, FlowLesson, Unit, \
    Teacher, Admin, ParticipantLesson, CourseLesson, Question, LessonResponse, Webinar
from djangoapps.lms_cms import constants
from djangoapps.lms_cms.models import FlowSchedule, FlowParticipants, CmsCourse, CmsLesson


class StudentsInline(admin.TabularInline):
    fields = ['user', 'notes']
    model = Student
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name=constants.STUDENTS_GROUP_NAME)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TeachersInline(admin.TabularInline):
    model = Teacher
    exclude = ['role']
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name=constants.TEACHERS_GROUP_NAME)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AdminsInline(admin.TabularInline):
    model = Admin
    exclude = ['role']
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name=constants.ADMINS_GROUP_NAME)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(FlowParticipants)
class FlowParticipantsAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'state', 'start_planned_at')
    readonly_fields = ['name', 'course', 'state', 'started_at', 'finished_at']
    fieldsets = (
        ('Properties', {
            'fields': ('name', 'course', 'state')
        }),
        ('Datetime', {
            'classes': ('collapse',),
            'fields': (('started_at', 'finished_at',),),
        }),
    )
    inlines = [AdminsInline, TeachersInline, StudentsInline]


class FlowLessonInline(SortableInlineAdminMixin, admin.TabularInline):
    model = FlowLesson
    extra = 0

    def get_formset(self, request, obj: Flow=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.course:
            formset.form.base_fields['unit'].queryset = Unit.objects.filter(course=obj.course)
            formset.form.base_fields['course_lesson'].queryset = CourseLesson.objects.filter(course=obj.course)
        return formset


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'state', 'start_planned_at')
    list_filter = ['state', 'course']
    exclude = ['group']
    readonly_fields = ['course', 'started_at', 'finished_at']
    search_fields = ('name', 'course')
    inlines = [FlowLessonInline]


class FlowLessonsForScheduleInline(admin.StackedInline):
    fields = ['number', 'lesson', 'is_opened', 'open_planned_at', 'opened_at']
    # Field 'is_opened' is readonly in order to lms_periodic command trigger open_lesson()
    readonly_fields = ['opened_at', 'is_opened', ]
    model = FlowLesson
    extra = 0


@admin.register(FlowSchedule)
class FlowScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'state', 'start_planned_at')
    list_filter = ['state']
    readonly_fields = ['name', 'started_at', 'finished_at']
    search_fields = ('name', 'course')
    fieldsets = (
        ('Properties', {
            'fields': ('name', 'state')
        }),
        ('Settings', {
            'fields': ('schedule_template', 'start_planned_at')
        }),
        ('Datetime', {
            'classes': ('collapse',),
            'fields': (('started_at', 'finished_at',),),
        }),
    )
    inlines = [FlowLessonsForScheduleInline]


class AttendanceInline(admin.TabularInline):
    model = ParticipantLesson
    fields = ['flow_lesson', 'check_result', 'score', 'is_completed', 'is_checked', 'when_checked']
    readonly_fields = ['flow_lesson', 'when_checked', 'is_completed', 'is_checked', ]
    extra = 0
    max_num = 1


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'notes', ]
    list_filter = ['flow', ]
    search_fields = [
        'user__email', 'user__username', 'user__username', 'user__first_name', 'user__last_name',
        'flow__name', 'notes',
    ]
    readonly_fields = ('user', 'flow')
    ordering = ['user__first_name', 'user__last_name']
    fieldsets = (
        (None, {
            'fields': ('user', 'flow', 'notes'),
        }),
    )
    inlines = [AttendanceInline]


class LessonQuestionAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='admin_config'))

    class Meta:
        model = Question
        fields = '__all__'


class LessonQuestionInline(admin.StackedInline):
    model = Question
    form = LessonQuestionAdminForm
    fieldsets = (
        (None, {
            'fields': (
                ('ordering', 'name', 'code', 'type', 'required', 'score'),
                ('text', 'choices'),
            ),
        }),
        ('Автопроверка', {
            # 'classes': ('collapse',),
            'fields': (('is_autocheck', 'correct_answer'),),
        }),
    )
    extra = 0


@admin.register(CmsLesson)
class LessonAdmin(PlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ['code', 'title']
    inlines = [LessonQuestionInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


class CourseLessonInline(SortableInlineAdminMixin, admin.TabularInline):
    model = CourseLesson
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.form.base_fields['unit'].queryset = Unit.objects.filter(course=obj)
        return formset


class CourseUnitInline(admin.TabularInline):
    model = Unit
    extra = 0


@admin.register(CmsCourse)
class CourseAdmin(PlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'code', 'state']
    inlines = [CourseUnitInline, CourseLessonInline]


@admin.register(LessonResponse)
class LessonResponseAdmin(admin.ModelAdmin):
    pass


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    pass

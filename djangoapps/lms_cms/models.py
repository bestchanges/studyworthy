import cms.api
from cms.models import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangoapps.lms.models import Lesson, Flow, Participant, FlowLesson, ParticipantLesson, CourseLesson, \
    Course


class CmsCourse(Course):
    icon = models.CharField(max_length=100, default='fas fa-graduation-cap')
    flow_content = PlaceholderField('flow_content', related_name='flow_content',
                                    help_text=_('Content shown on the flow index page'))
    common_content = PlaceholderField('lesson_common_content', related_name='lesson_common_content',
                                      help_text=_('Content shown in each course lesson'))

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if is_create:
            cms.api.add_plugin(
                placeholder=self.flow_content,
                plugin_type='CourseLessonsCMSPlugin',
                language='ru',
            )
            cms.api.add_plugin(
                placeholder=self.common_content,
                plugin_type='CommentsCMSPlugin',
                language='ru',
            )


class CmsLesson(Lesson):
    lesson_content = PlaceholderField('lesson_content', related_name='lesson_content')
    support_content = PlaceholderField('support_content', related_name='support_content')
    show_common_content = models.BooleanField(
        default=True,
        help_text=_('Display content common for all lessons across course at the bottom of lesson content'))

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        if is_create:
            cms.api.add_plugin(
                placeholder=self.lesson_content,
                plugin_type='PageTitleCMSPlugin',
                language='ru',
            )
            cms.api.add_plugin(
                placeholder=self.lesson_content,
                plugin_type='TextCMSPlugin',
                language='ru',
                body=f'<h2>В этом уроке:</h2>{self.brief}',
            )
            cms.api.add_plugin(
                placeholder=self.lesson_content,
                plugin_type='VideoYoutubeCMSPlugin',
                language='ru',
            )


class CommentsConfigCMSPlugin(CMSPlugin):
    ATTACH_COURSE = 'Course'
    ATTACH_FLOW = 'Flow'

    CHOICES = [
        (ATTACH_COURSE, _('Attach to course')),
        (ATTACH_FLOW, _('Attach to flow')),
    ]

    attach_to = models.CharField(max_length=20, choices=CHOICES, default=ATTACH_FLOW)


class VideoYoutubeConfigCMSPlugin(CMSPlugin):
    youtube_id = models.CharField(max_length=250, default='')


class HtmlCMSPluginConfig(CMSPlugin):
    content = models.TextField(default='')


class LessonNavigationCMSPluginConfig(CMSPlugin):
    pass


class CourseLessonsConfigCMSPlugin(CMSPlugin):
    pass


class PageRowColumnConfigCMSPlugin(CMSPlugin):
    pass


def participant_directory(instance, filename):
    return 'participants/{0}/{1}'.format(instance.participant.id, filename)


class Comment(models.Model):
    RESULT_ACCEPTED = ParticipantLesson.RESULT_ACCEPTED
    RESULT_FAILED = ParticipantLesson.RESULT_FAILED
    RESULT_REJECTED = ParticipantLesson.RESULT_REJECTED

    CHOICES_RESULT = (
        (None, _('Just comment')),
        (RESULT_ACCEPTED, _('Accepted')),
        (RESULT_FAILED, _('Failed')),
        (RESULT_REJECTED, _('Rejected')),
    )

    flow_lesson = models.ForeignKey(FlowLesson, null=True, on_delete=models.CASCADE, related_name='discussions',
                                    help_text='Discussion attached to Flow Lesson')
    course_lesson = models.ForeignKey(CourseLesson, null=True, on_delete=models.CASCADE, related_name='discussions',
                                      help_text='Discussion attached to the Course Lesson')
    participant = models.ForeignKey(Participant, null=True, on_delete=models.SET_NULL, related_name='+')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')

    comment = models.TextField(default='', verbose_name=_('Your answer'))
    file = models.FileField(null=True, blank=True, upload_to=participant_directory)
    hide_from_others = models.BooleanField(default=False, verbose_name=_('Hide from others'))

    check_result = models.CharField(blank=True, null=True, choices=CHOICES_RESULT,
                                    max_length=30,
                                    verbose_name=_('Check result'))
    score = models.IntegerField(default=None, null=True, blank=True,
                                verbose_name=_('Score'), help_text=_('Score for student response'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def teacher_check(self):
        """return True if check_result is RESULT_ACCEPTED"""
        return self.check_result == self.RESULT_ACCEPTED

    def allow_thread(self):
        return self.parent is None

    class Meta:
        ordering = ['updated_at']


class FlowSchedule(Flow):
    """We need separate AdminForm for scheduling"""

    class Meta:
        proxy = True
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')


class FlowParticipants(Flow):
    """We need separate AdminForm for participants"""

    class Meta:
        proxy = True
        verbose_name = _('Participants')
        verbose_name_plural = _('Participnts')

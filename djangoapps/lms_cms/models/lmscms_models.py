from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangoapps.lms.models.lms_models import Lesson, Flow, Participant, FlowLesson, Attendance


class CommentsConfigCMSPlugin(CMSPlugin):
    ATTACH_COURSE = 'Course'
    ATTACH_FLOW = 'Flow'

    attach_to = models.CharField(
        max_length=20,
        choices=[(choice, _(choice)) for choice in (ATTACH_COURSE, ATTACH_FLOW)],
        default=ATTACH_FLOW
    )


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
    RESULT_ACCEPTED = Attendance.RESULT_ACCEPTED
    RESULT_FAILED = Attendance.RESULT_FAILED
    RESULT_REJECTED = Attendance.RESULT_REJECTED

    CHOICES_RESULT = (
        (None, _('Just comment')),
        (RESULT_ACCEPTED, _('Accepted')),
        (RESULT_FAILED, _('Failed')),
        (RESULT_REJECTED, _('Rejected')),
    )

    flow_lesson = models.ForeignKey(FlowLesson, null=True, on_delete=models.CASCADE, related_name='discussions',
                                    help_text='Discussion attached to this object')
    lesson = models.ForeignKey(Lesson, null=True, on_delete=models.CASCADE, related_name='discussions',
                               help_text='Discussion attached to this object')
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

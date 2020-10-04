import mimetypes

from cms.models import Page
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from djangocms_bootstrap4.contrib.bootstrap4_picture.cms_plugins import Bootstrap4PicturePlugin
from djangocms_file.cms_plugins import FilePlugin
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from djangoapps.lms.models.lms_models import Student, Participant, FlowLesson, StudentLesson, Flow, Course
from djangoapps.lms_cms.forms import create_comment_form
from djangoapps.lms_cms.models.lmscms_models import VideoYoutubeConfigCMSPlugin, \
    CommentsConfigCMSPlugin, CourseLessonsConfigCMSPlugin, Comment, \
    PageRowColumnConfigCMSPlugin, HtmlCMSPluginConfig, LessonNavigationCMSPluginConfig


@plugin_pool.register_plugin
class CommentsCMSPlugin(CMSPluginBase):
    model = CommentsConfigCMSPlugin
    name = _('Comments')
    render_template = "lms_cms/cms_plugins/comments.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance: CommentsConfigCMSPlugin, placeholder):
        request = context['request']
        context = super(CommentsCMSPlugin, self).render(context, instance, placeholder)
        page: Page = instance.page
        lesson = LmsPage.get_lesson(page)
        if not lesson:
            return context

        participant: Participant = request.lms_participant if hasattr(request, 'lms_participant') else None  # noqa
        if not participant:
            return context

        # Deal with the form
        flow = participant.flow
        flow_lesson = FlowLesson.objects.filter(lesson=lesson, flow=flow).first()
        if not flow_lesson:
            return context

        context['flow_lesson'] = flow_lesson
        Form = create_comment_form(participant=participant, parent=None)
        comment = Comment(
            flow_lesson=flow_lesson,
        )
        form = Form(instance=comment)
        context['form'] = form
        # Now display comments tree
        q_attached_to = Q()
        if instance.attach_to == instance.ATTACH_FLOW:
            q_attached_to = Q(flow_lesson=flow_lesson)
        elif instance.attach_to == instance.ATTACH_COURSE:
            q_attached_to = Q(lesson=lesson)

        my_comments = Comment.objects.filter(
            q_attached_to,
            participant=participant,
            parent=None,
        ).order_by('-updated_at')
        others_comments = Comment.objects.filter(
            q_attached_to,
            ~Q(participant=participant),
            parent=None,
        ).order_by('-updated_at')

        if participant and participant.role == Participant.ROLE_STUDENT:
            # hide from other students
            others_comments = others_comments.filter(hide_from_others=False)

        context['others_comments'] = others_comments
        context['my_comments'] = my_comments
        context['page'] = page

        # save page_id for comments
        request.session['comment_return_page'] = page.get_absolute_url()

        if instance.attach_to == instance.ATTACH_FLOW:
            context['object'] = participant.flow
        elif instance.attach_to == instance.ATTACH_COURSE:
            context['object'] = participant.flow.course

        return context


@plugin_pool.register_plugin
class CourseLessonsCMSPlugin(CMSPluginBase):
    """
    List of lessons in the current course.
    Can only be displayed if 'student' in context.
    """
    model = CourseLessonsConfigCMSPlugin
    name = _('Flow lessons')
    render_template = "lms_cms/cms_plugins/flow_lessons.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance, placeholder):
        context = super(CourseLessonsCMSPlugin, self).render(context, instance, placeholder)
        student: Student = context['student']
        assert student, 'no student in context'
        # current_user: User = context['request'].user
        context['role'] = 'STUDENT'
        return context


class AddPageBlockIfRootPlugin(CMSPluginBase):
    def render(self, context, instance, placeholder):
        if instance.parent:
            base_template = 'lms_cms/cms_plugins/layout-dummy.html'
        else:
            base_template = 'lms_cms/cms_plugins/layout-block.html'
        context['base_template'] = base_template
        return super(AddPageBlockIfRootPlugin, self).render(context, instance, placeholder)


@plugin_pool.register_plugin
class PageTitleCMSPlugin(AddPageBlockIfRootPlugin):
    """Page title."""
    name = _('Page Title')
    render_template = "lms_cms/cms_plugins/page_title.html"
    module = _(' LMS Content')
    cache = True

    def render(self, context, instance, placeholder):
        context['title'] = instance.page.get_title()
        context = super(PageTitleCMSPlugin, self).render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class BlockCMSPlugin(AddPageBlockIfRootPlugin):
    """Page title."""
    name = _('Block')
    render_template = "lms_cms/cms_plugins/block.html"
    module = _(' LMS Content')
    cache = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context['title'] = instance.page.get_title()
        context = super(BlockCMSPlugin, self).render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class LessonCompleteCMSPlugin(AddPageBlockIfRootPlugin):
    name = _('Lesson completed')
    render_template = "lms_cms/cms_plugins/lesson_completed_button.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance, placeholder):
        participant: Participant = context['request'].lms_participant
        page: Page = instance.page
        lesson = LmsPage.get_lesson(page)
        assert lesson, "can be used only on lesson pages"
        attendance = StudentLesson.objects.filter(participant=participant, flow_lesson__lesson=lesson).first()
        context['attendance'] = attendance
        context = super(AddPageBlockIfRootPlugin, self).render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class LessonNavigationCMSPlugin(CMSPluginBase):
    name = _('Lesson navigation bar')
    render_template = "lms_cms/cms_plugins/lesson_navbar.html"
    module = _(' LMS Control')
    model = LessonNavigationCMSPluginConfig
    cache = False

    def render(self, context, instance, placeholder):
        page: Page = instance.page
        course = LmsPage.get_course_any(page)
        assert course, "can be used only on lesson pages"
        course_page = LmsPage.page_for_course(course)
        context['course'] = course
        context['course_page'] = course_page
        return context


@plugin_pool.register_plugin
class TextCMSPlugin(AddPageBlockIfRootPlugin, TextPlugin):
    name = _('Text')
    module = _(' LMS Content')
    render_template = 'lms_cms/cms_plugins/text.html'
    cache = True

    def render(self, context, instance, placeholder):
        context = super(TextCMSPlugin, self).render(context, instance, placeholder)
        if not hasattr(instance, "page") or not instance.page:
            title = "No title"
        else:
            title = instance.page.get_title()
        context['title'] = title
        context = super(AddPageBlockIfRootPlugin, self).render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class HTMLCMSPlugin(CMSPluginBase):
    name = _('HTML code')
    module = _(' LMS Content')
    render_template = 'lms_cms/cms_plugins/html_code.html'
    cache = True
    model = HtmlCMSPluginConfig
    allow_children = False

    def render(self, context, instance, placeholder):
        context['html'] = instance.content
        return context


@plugin_pool.register_plugin
class PageRowColumnCMSPlugin(CMSPluginBase):
    name = _('Columns')
    module = _(' LMS Content')
    cache = True
    model = PageRowColumnConfigCMSPlugin
    render_template = "lms_cms/cms_plugins/row_columns.html"
    allow_children = True


@plugin_pool.register_plugin
class ImageCMSPlugin(Bootstrap4PicturePlugin):
    name = _('Image')
    module = _(' LMS Content')
    cache = True


@plugin_pool.register_plugin
class VideoYoutubeCMSPlugin(AddPageBlockIfRootPlugin, CMSPluginBase):
    model = VideoYoutubeConfigCMSPlugin
    name = _('Video Youtube')
    module = _(' LMS Content')
    render_template = "lms_cms/cms_plugins/video_youtube.html"
    cache = True

    def render(self, context, instance, placeholder):
        context = super(AddPageBlockIfRootPlugin, self).render(context, instance, placeholder)
        context = super(VideoYoutubeCMSPlugin, self).render(context, instance, placeholder)
        return context


@plugin_pool.register_plugin
class FileCMSPlugin(AddPageBlockIfRootPlugin, FilePlugin):
    name = _('File (+audio)')
    module = _(' LMS Content')
    render_template = "lms_cms/cms_plugins/file.html"
    cache = True

    def render(self, context, instance: FilePlugin, placeholder):
        context = super(AddPageBlockIfRootPlugin, self).render(context, instance, placeholder)
        context = super(FileCMSPlugin, self).render(context, instance, placeholder)

        filename = instance.file_src.original_filename if instance.file_src else ''
        file_mime = mimetypes.guess_type(filename)[0]
        if file_mime and file_mime.startswith('audio/'):
            context['is_audio'] = True
        return context

    def get_render_template(self, context, instance, placeholder):
        return self.render_template

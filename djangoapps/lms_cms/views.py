from django import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from djangoapps.lms.models.lms_models import Participant, Attendance
from djangoapps.lms_cms.forms import create_comment_form
from djangoapps.lms_cms.models.lmscms_models import Comment


def comment_add(request):
    BaseCommentForm = forms.modelform_factory(
        model=Comment,
        fields=['parent', 'flow_lesson'],
    )
    if request.GET:
        form = BaseCommentForm(request.GET)
    else:
        form = BaseCommentForm(request.POST, request.FILES)
    assert form.is_valid(), str(form.errors)

    flow_lesson = form.cleaned_data['flow_lesson']
    participant: Participant = request.lms_participant
    assert participant.flow == flow_lesson.flow, "Participant cannot comment here"
    requested_parent = form.cleaned_data['parent']
    parent = requested_parent
    if parent:
        # only one level comments allowed, so attach to root comment
        for _ in range(3):
            if not parent.parent:
                break
            parent = parent.parent
        else:
            raise ValueError(f"Cannot find root comment for {form.parent}")
    comment = Comment(
        participant=participant,
        flow_lesson=flow_lesson,
        lesson=flow_lesson.lesson,
        parent=parent,
    )
    CommentForm = create_comment_form(participant=participant, parent=parent)
    form = CommentForm(request.POST or None, request.FILES or None, instance=comment)
    if request.POST and form.is_valid():
        comment_model: Comment = form.save()

        if comment.parent and participant.role in [Participant.ROLE_TEACHER, Participant.ROLE_ADMIN]:
            student_participant = comment.parent.participant
            student_attendance = Attendance.objects.get(flow_lesson=flow_lesson, participant=student_participant)
            if comment.check_result:
                student_attendance.check_result = comment.check_result
                student_attendance.when_checked = timezone.now()
            if comment.score is not None:
                student_attendance.score = comment.score
            student_attendance.save()

        lesson_page = LmsPage.page_for_lesson(comment_model.flow_lesson.lesson)
        redirect_url = lesson_page.get_absolute_url()
        return redirect(f"{redirect_url}#c{comment_model.id}")
    context = {
        'source': requested_parent,
        'form': form,
    }
    return render(request, "lms_cms/comments/reply.html", context)


def attendance_completed(request, attendance_id):
    """Mark attandance as completed. Called by AJAX request from cms_plogins.LessonCompleteCMSPlugin"""
    current_user = request.user
    attendance = Attendance.objects.get(pk=attendance_id)
    value = request.GET['value']
    assert attendance.participant.user == current_user, \
        f"Attendance participant {attendance.participant.pk} is not current user"
    attendance.when_completed = now() if value == 'true' else None
    attendance.save()
    return HttpResponse(f'OK Completed: {attendance.is_completed}')
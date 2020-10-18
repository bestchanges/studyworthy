from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from djangoapps.erp.models import Order, Person
from djangoapps.lms.forms import StudentResponseForm
from djangoapps.lms.models import Participant, ParticipantLesson, Student, LessonResponse
from djangoapps.lms_cms.forms import create_comment_form
from djangoapps.lms_cms.models import Comment


def comment_add(request):
    BaseCommentForm = forms.modelform_factory(
        model=Comment,
        fields=['parent', 'flow_lesson', 'participant'],
    )
    if request.GET:
        form = BaseCommentForm(request.GET)
    else:
        form = BaseCommentForm(request.POST, request.FILES)
    assert form.is_valid(), str(form.errors)

    flow_lesson = form.cleaned_data['flow_lesson']
    participant: Participant = form.cleaned_data['participant']
    assert participant.flow == flow_lesson.flow, "Participant cannot comment here"
    # TODO: security: check current user
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
        course_lesson=flow_lesson.course_lesson,
        parent=parent,
    )
    CommentForm = create_comment_form(participant=participant, parent=parent)
    form = CommentForm(request.POST or None, request.FILES or None, instance=comment)
    if request.POST and form.is_valid():
        comment_model: Comment = form.save()

        if comment.parent and participant.role in [Participant.ROLE_TEACHER, Participant.ROLE_ADMIN]:
            student_participant = comment.parent.participant
            student_attendance = ParticipantLesson.objects.get(flow_lesson=flow_lesson, participant=student_participant)
            if comment.check_result:
                student_attendance.check_result = comment.check_result
                student_attendance.when_checked = timezone.now()
            if comment.score is not None:
                student_attendance.score = comment.score
            student_attendance.save()

        redirect_url = request.session.get('comment_return_page')
        if not redirect_url:
            redirect_url = reverse('lesson-view', kwargs={"participant_id": participant.id})
        return redirect(f"{redirect_url}#comment{comment_model.id}")
    context = {
        'source': requested_parent,
        'form': form,
    }
    return render(request, "lms_cms/comments/reply.html", context)


# @by_student_only
def attendance_completed(request, participant_lesson_id):
    """Mark attandance as completed. Called by AJAX request from cms_plogins.LessonCompleteCMSPlugin"""
    current_user = request.user
    attendance = ParticipantLesson.objects.get(pk=participant_lesson_id)
    value = request.GET['value']
    assert attendance.participant.user == current_user, \
        f"Attendance participant {attendance.participant.pk} is not current user"
    attendance.when_completed = now() if value == 'true' else None
    attendance.save()
    return HttpResponse(f'OK Completed: {attendance.is_completed}')


@login_required
def student_kabinet(request):
    user = request.user

    student_in = Student.objects.filter(user=user).all()
    person = Person.objects.filter(user=user).first()
    if person and False:
        client_orders = Order.objects.filter(client=person).exclude(state__in=Order.FINAL_STATES)
    else:
        client_orders = []
    context = {
        "student_in": student_in,
        "client_orders": client_orders,
    }
    return render(request, "lms_cms/student_courses.html", context)


@login_required
def flow_view(request, flow_id):
    participant = Participant.objects.filter(flow_id=flow_id, user=request.user).first()
    if not participant:
        raise PermissionDenied(_('Not participant'))
    flow = participant.flow
    context = {
        "flow": flow,
        "course": flow.course.cmscourse,
        "student": participant.student,
        "participant": participant,
    }
    return render(request, "lms_cms/flow.html", context)


@login_required
def lesson_view(request, flow_lesson_id):
    participant_lesson = ParticipantLesson.objects.filter(
        flow_lesson_id=flow_lesson_id, participant__user=request.user
    ).first()
    if not participant_lesson:
        raise PermissionDenied('User not participant or flow not exist')
    flow_lesson = participant_lesson.flow_lesson
    flow = flow_lesson.flow
    participant = participant_lesson.participant

    form = StudentResponseForm(request.POST or None, lesson=flow_lesson.lesson)
    if form.is_bound:
        lesson_response: LessonResponse = form.save(commit=False)
        lesson_response.participant_lesson = participant_lesson
        lesson_response.save()
    helper = FormHelper()
    helper.form_method = 'post'
    # helper.form_style = 'inline'
    # helper.form_action = reverse('lms_cms:comment_reply')
    helper.add_input(Submit('submit', _('Submit')))
    # helper.help_text_inline = True
    # helper.html5_required = True
    form.helper = helper

    context = {
        "participant_lesson": participant_lesson,
        "flow_lesson": flow_lesson,
        "lesson": flow_lesson.lesson.cmslesson,
        "flow": flow,
        "course": flow.course.cmscourse,
        "student": participant.student,
        "participant": participant,
        "questions_form": form,
    }
    return render(request, "lms_cms/flow_lesson.html", context)

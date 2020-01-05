from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lms.models.content import Unit
from lms.models.learning import Learning, Lesson, Participant
from rootapp.models import SiteUser


@login_required
def index(request):
    user: SiteUser = request.user
    my_learnings = Learning.objects.filter(state__in=(Learning.State.ONGOING, Learning.State.PLANNED),
                                           participant__person=user.person)
    return render(request, 'campus/index.html', {'learnings': my_learnings})


@login_required
def learning_view(request, learning_code):
    learning: Learning = Learning.objects.get_by_natural_key(learning_code)
    context = {
        'learning': learning,
        'lessons': learning.lesson_set.all(),
        'students': learning.participant_set.filter(role=Participant.Role.STUDENT),
        'teachers': learning.participant_set.filter(role=Participant.Role.TEACHER),
        'admins': learning.participant_set.filter(role=Participant.Role.ADMIN),
    }
    return render(request, 'campus/learning.html', context)


@login_required
def lesson_view(request, learning_code, unit_slug):
    learning = Learning.objects.get_by_natural_key(learning_code)
    unit = Unit.objects.get(course=learning.course, slug=unit_slug)
    lesson = Lesson.objects.get(learning=learning, unit=unit)
    return render(request, 'campus/lesson.html', {'lesson': lesson, 'unit': unit, 'learning': learning})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from lms.models.content import Unit
from lms.models.learning import Learning, Lesson
from rootapp.models import SiteUser


@login_required
def index(request):
    user: SiteUser = request.user
    my_learnings = user.person.learn_in.all()
    return render(request, 'campus/index.html', {'learnings': my_learnings})


@login_required
def learning_view(request, learning_code):
    learning: Learning = Learning.objects.get_by_natural_key(learning_code)
    context = {
        'learning': learning,
        'lessons': learning.lesson_set.all(),
        'students': learning.students.all(),
        'teachers': learning.teachers.all(),
        'admin': learning.admin,
    }
    return render(request, 'campus/learning.html', context)


@login_required
def lesson_view(request, learning_code, unit_slug):
    learning = Learning.objects.get_by_natural_key(learning_code)
    unit = Unit.objects.get(course=learning.course, slug=unit_slug)
    lesson = Lesson.objects.get(learning=learning, unit=unit)
    return render(request, 'campus/lesson.html', {'lesson': lesson, 'unit': unit, 'learning': learning})

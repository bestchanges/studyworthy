from django.utils import timezone

from lms.models.learning import Learning, Lesson
# TODO: do not like this design. No app shall depend on existence of property in settings. No way!
from studyworthy.settings_default import PERIODIC_PERIOD_TIMEDELTA


def periodic_task_start_learnings():
    now = timezone.now()
    ready_to_start = list(Learning.objects.filter(
        state=Learning.State.PLANNED,
        start_planned_at__lte=now,
        start_planned_at__gte=now - PERIODIC_PERIOD_TIMEDELTA
    ))
    for learning in ready_to_start:
        learning.state = learning.State.ONGOING
        learning.save()
    return ready_to_start


def periodic_task_open_lessons():
    now = timezone.now()
    ready_to_start = list(Lesson.objects.filter(
        state=Lesson.State.CLOSED,
        open_planned_at__lte=now,
        open_planned_at__gte=now - PERIODIC_PERIOD_TIMEDELTA
    ))
    for lesson in ready_to_start:
        lesson.state = Lesson.State.OPENED
        lesson.save()
    return ready_to_start

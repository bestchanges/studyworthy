import logging
from datetime import timedelta

from django.utils.timezone import now

from djangoapps.lms.models.lms_models import FlowLesson, Flow


def flows_start_ready():
    """Change state of flows ready to be started. """
    logging.info(f'Flows ')
    for flow in Flow.objects.filter(
            start_planned_at__lte=now(),
            start_planned_at__gte=now() - timedelta(days=15),
            state__in=[Flow.STATE_PLANNED],
    ):
        logging.info(f'Flow {flow}')
        flow.start_flow()


def lessons_open_ready():
    """Opens the flow_lessons which are ready to be open. """
    for flow_lesson in FlowLesson.objects.filter(
            opened_at=None,
            open_planned_at__lte=now(),
            open_planned_at__gte=now() - timedelta(days=14),
            flow__state__in=[Flow.STATE_ONGOING]
    ):
        flow_lesson.open_lesson()

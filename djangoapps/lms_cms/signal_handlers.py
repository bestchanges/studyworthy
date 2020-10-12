from django.db.models.signals import post_save
from django.dispatch import receiver

from djangoapps.lms.models import FlowLesson, Participant
from djangoapps.lms.signals import lesson_available, lesson_unavailable
from djangoapps.lms_cms import email


@receiver(lesson_available, sender=FlowLesson)
def on_lesson_available(sender, flow_lesson: FlowLesson, **kwargs):
    email.send_notification_lesson_open(flow_lesson=flow_lesson)


@receiver(lesson_unavailable, sender=FlowLesson)
def on_lesson_unavailable(sender, flow_lesson: FlowLesson, **kwargs):
    pass


# handle all models in order to get all Participant subclasses
@receiver(post_save)
def on_create_participant(sender, instance: Participant, created: bool, raw: bool, **kwargs):
    if not issubclass(sender, Participant):
        return
    if created and not raw:
        if instance.user.email:
            email.send_notification_enrolled_to_flow(instance)

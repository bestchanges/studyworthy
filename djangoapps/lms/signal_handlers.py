from django.db.models.signals import post_delete
from django.dispatch import receiver

from djangoapps.lms.models.lms_models import Flow, Student, Participant


@receiver(post_delete, sender=Flow)
def on_flow_delete(sender, instance: Flow, **kwargs):
    if instance.group:
        instance.group.delete()


@receiver(post_delete, sender=Participant)
def on_participant_delete(sender, instance: Participant, **kwargs):
    """On Participant removal need to delete his user from flow group"""
    if instance.flow.group:
        instance.user.groups.remove(instance.flow.group)

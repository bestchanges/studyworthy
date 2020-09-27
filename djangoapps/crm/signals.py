import logging

from django.dispatch import receiver

from djangoapps.common.signals import state_changed
from djangoapps.crm.models.erp_models import Invoice

logger = logging.getLogger(__name__)

@receiver(state_changed)  #, sender=Invoice
def on_state_changed(sender, instance, old_state, **kwargs):
    logger.info(f'New state "{str(instance.state)}" for {instance} (old state "{old_state}")')
import logging

from django.dispatch import receiver

from djangoapps.crm.models.erp_models import Invoice
from djangoapps.crm.signals import state_changed

logger = logging.getLogger(__name__)

@receiver(state_changed, sender=Invoice)
def on_state_changed(sender, old_state, **kwargs):
    logger.info(f'New state "{str(sender.state)}" for {sender} (old state "{old_state}")')
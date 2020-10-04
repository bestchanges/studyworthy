import logging

from django.dispatch import receiver

from djangoapps.erp.models import ClientOrder
from djangoapps.erp.signals import state_changed

logger = logging.getLogger(__name__)


@receiver(state_changed, sender=ClientOrder)
def on_client_order_state_change(sender, instance: ClientOrder, old_state, **kwargs):
    client_order = instance
    if client_order.state == ClientOrder.State.PROCESSING:
        # This is signal from fulfillment
        for item in client_order.items.all():
            courseproduct = getattr(item.product, "courseproduct")
            if courseproduct:
                courseproduct.enroll_from_client_order(client_order)
        client_order.set_state(ClientOrder.State.COMPLETED)
    else:
        # let's check if we need to start processing
        order_state_to_event = {
            ClientOrder.State.NEW: ClientOrder.FulfillOn.CREATED,
            ClientOrder.State.CONFIRMED: ClientOrder.FulfillOn.CONFIRMED,
        }
        event_name = order_state_to_event.get(client_order.state)
        if event_name and client_order.fulfill_on == event_name:
            logger.info(
                f"Initiate fulfillment for {client_order} (order state={client_order.state}, fulfill_on={client_order.fulfill_on}")
            client_order.fulfill()

import logging

from django.dispatch import receiver

from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Order
from djangoapps.erp.signals import state_changed

logger = logging.getLogger(__name__)


@receiver(state_changed, sender=Order)
def on_client_order_state_change(sender, instance: Order, old_state, **kwargs):
    order = instance
    if order.state == Order.State.PROCESSING:
        # This is signal from fulfillment
        enrolled = False
        for item in order.items.all():
            course_product = CourseProduct.objects.filter(pk=item.product.pk).first()
            if course_product:
                course_product.enroll_from_client_order(order)
                enrolled = True
        if enrolled:
            order.set_state(Order.State.COMPLETED)
        else:
            logger.error(f'Cannot process order {order}. There are no any CourseProducts in it.')
    else:
        # let's check if we need to start processing
        order_state_to_event = {
            Order.State.NEW: Order.FulfillOn.CREATED,
            Order.State.CONFIRMED: Order.FulfillOn.CONFIRMED,
        }
        event_name = order_state_to_event.get(order.state)
        if event_name and order.fulfill_on == event_name:
            logger.info(
                f"Initiate fulfillment for {order} (order state={order.state}, fulfill_on={order.fulfill_on}")
            order.fulfill()

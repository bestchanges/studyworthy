import logging

from django.dispatch import receiver

from djangoapps.erp.models import Order, Invoice, Payment
from djangoapps.erp.signals import state_changed

logger = logging.getLogger(__name__)


@receiver(state_changed)
def log_state_change(sender, instance, old_state, **kwargs):
    logger.info(f'New state "{str(instance.state)}" for {sender.__name__} {instance} (old state "{old_state}")')


@receiver(state_changed, sender=Payment)
def on_paymentin_state_change(sender, instance: Payment, old_state, **kwargs):
    if not instance.invoice:
        return
    invoice = instance.invoice
    payed_amount = invoice.payed_amount
    if payed_amount:
        if payed_amount >= invoice.amount:
            invoice.set_state(Invoice.State.PAYED_FULLY)
        else:
            invoice.set_state(Invoice.State.PAYED_PARTLY)
    else:
        invoice.set_state(Invoice.State.WAITING)


@receiver(state_changed, sender=Invoice)
def on_invoice_state_change(sender, instance: Invoice, old_state, **kwargs):
    # if invoice to CourseProduct fully payed then enroll student
    invoice = instance
    order = invoice.order
    if not order or not order.fulfill_on:
        return
    invoice_state_to_events = {
        Invoice.State.PAYED_FULLY: [Order.FulfillOn.ORDER_PAYED_FULL, Order.FulfillOn.ORDER_PAYED_PARTLY],
        Invoice.State.PAYED_PARTLY: [Order.FulfillOn.ORDER_PAYED_PARTLY],
    }
    fulfill_on_events = invoice_state_to_events.get(invoice.state, [])
    if order.fulfill_on in fulfill_on_events:
        logger.info(f"Initiate fulfillment for {order} (order: {order.state}, invoice: {invoice.state}")
        order.fulfill()

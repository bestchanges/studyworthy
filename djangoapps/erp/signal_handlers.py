import logging

from django.dispatch import receiver

from djangoapps.erp.models import ClientOrder, Invoice, PaymentIn
from djangoapps.erp.signals import state_changed

logger = logging.getLogger(__name__)


@receiver(state_changed)
def log_state_change(sender, instance, old_state, **kwargs):
    logger.info(f'New state "{str(instance.state)}" for {sender.__name__} {instance} (old state "{old_state}")')


@receiver(state_changed, sender=PaymentIn)
def on_paymentin_state_change(sender, instance: PaymentIn, old_state, **kwargs):
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
    client_order = invoice.client_order
    if not client_order or not client_order.fulfill_on:
        return
    invoice_state_to_events = {
        Invoice.State.PAYED_FULLY: [ClientOrder.FulfillOn.ORDER_PAYED_FULL, ClientOrder.FulfillOn.ORDER_PAYED_PARTLY],
        Invoice.State.PAYED_PARTLY: [ClientOrder.FulfillOn.ORDER_PAYED_PARTLY],
    }
    fulfill_on_events = invoice_state_to_events.get(invoice.state, [])
    if client_order.fulfill_on in fulfill_on_events:
        logger.info(f"Initiate fulfillment for {client_order} (order: {client_order.state}, invoice: {invoice.state}")
        client_order.fulfill()


@receiver(state_changed, sender=ClientOrder)
def on_client_order_state_change(sender, instance: ClientOrder, old_state, **kwargs):
    client_order = instance
    order_state_to_event = {
        ClientOrder.State.NEW: ClientOrder.FulfillOn.CREATED,
        ClientOrder.State.CONFIRMED: ClientOrder.FulfillOn.CONFIRMED,
    }
    event_name = order_state_to_event.get(client_order.state)
    if event_name and client_order.fulfill_on == event_name:
        logger.info(
            f"Initiate fulfillment for {client_order} (order state={client_order.state}, fulfill_on={client_order.fulfill_on}")
        client_order.fulfill()

import logging

from django.dispatch import receiver

from djangoapps.common.signals import state_changed
from djangoapps.crm.models.crm_models import ACTIONS
from djangoapps.crm.models.erp_models import Invoice, PaymentIn, ClientOrder

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
    if invoice.state == Invoice.State.PAYED_FULLY and client_order:
        for product_item in client_order.items.all():
            action_code = product_item.product.courseproduct.on_invoice_payed
            if action_code:
                method = ACTIONS[ClientOrder][action_code]['method']
                method(client_order)


@receiver(state_changed, sender=ClientOrder)
def on_client_order_state_change(sender, instance: ClientOrder, old_state, **kwargs):
    client_order = instance
    if client_order.state == client_order.State.NEW:
        for product_item in client_order.items.all():
            action_code = product_item.product.courseproduct.on_order_new
            if action_code:
                method = ACTIONS[ClientOrder][action_code]['method']
                method(client_order)

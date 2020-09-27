import datetime
import logging

from djangoapps.crm.api import yandex_kassa
from djangoapps.crm.models.erp_models import Invoice, PaymentIn

logger = logging.getLogger(__name__)


def create_yandex_payment_from_invoice(invoice: Invoice):
    description = f"Заказ #{invoice.document_number} от {invoice.document_date}"
    payment_in = PaymentIn.objects.create(
        payer=invoice.client,
        invoice=invoice,
        amount=invoice.amount,
        description=description
    )
    yandex_payment = yandex_kassa.create_payment(
        amount=str(payment_in.amount.amount),
        currency=str(payment_in.amount.currency.code),
        description=description,
        auto_capture=True,
        return_url="https://ya.ru",
    )

    payment_in.gateway_payment_id = yandex_payment.id
    # get confirmation url
    confirmation_url = yandex_payment.confirmation.confirmation_url
    payment_in.gateway_payment_url = confirmation_url
    payment_in.save()

    return payment_in


def update_status_yandex_payments():
    """List recent payments and update PaymentIn statuses."""
    payments = yandex_kassa.list_recent_payments(duration=datetime.timedelta(days=3))
    status_mapping = {
        'waiting_for_capture': PaymentIn.State.PROCESSED,
        'succeeded': PaymentIn.State.PROCESSED,
        'pending': PaymentIn.State.WAITING,
        'canceled': PaymentIn.State.CANCELLED,
    }
    for payment in payments:
        payment_id = payment.id
        assert payment_id
        payment_status = payment.status
        mapped_status = status_mapping.get(payment_status)
        if not mapped_status:
            logger.error(f'Cannot map status {payment_status} for yandex kassa payment {payment_id}')
            continue

        payment_in = PaymentIn.objects.filter(gateway_payment_id=payment_id).first()
        if not payment_in:
            logger.warning(f'Cannot find PaymentIn for yandex kassa payment {payment_id}')
            continue

        logger.info(f'Processing yandex kassa payment {payment_id}, PaymentIn {payment_in}')
        if payment_in.state != mapped_status:
            logger.info(f'Update state {payment_id}')
            payment_in.state = mapped_status
            payment_in.save()


def run_periodic():
    update_status_yandex_payments()
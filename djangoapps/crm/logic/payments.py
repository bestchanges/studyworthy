import datetime
import logging

from django.utils import timezone
from djmoney.money import Money
from yandex_checkout import PaymentResponse

from djangoapps.crm.api import yandex_kassa
from djangoapps.erp.models import PaymentIn

YANDEX_KASSA_PAYMENT_GATEWAY = 'yandex-kassa'

logger = logging.getLogger(__name__)


def pay_by_yandex_kassa(paymentin: PaymentIn, seccess_url):
    """
    Create Payment object for Yandex Kassa for given Payment and save it's status
    After this call the user should be directed to returned URL.
    Note: payment_in object will be saved.

    :param paymentin: Not yet payed, positive amount, with empty payment_gateway PaymentIn
    :param seccess_url: Full URL to which user shall be redirected after payment.
    :return: payment URL
    """
    assert paymentin.payment_gateway in (None, '', YANDEX_KASSA_PAYMENT_GATEWAY), \
        f"Payment gateway '{paymentin.payment_gateway}' not applicable for {paymentin}"
    assert paymentin.amount and paymentin.amount.amount > 0, \
        f"Inappropriate amount {paymentin.amount} for {paymentin}"
    assert paymentin.state in [PaymentIn.State.WAITING, PaymentIn.State.NEW], \
        f"Inappropriate state {paymentin.state} for {paymentin}"
    assert not paymentin.gateway_payment_id, \
        f"Yandex payment {paymentin.gateway_payment_id} is already created for {paymentin}"

    yk_payment = yandex_kassa.create_payment(
        amount=str(paymentin.amount.amount),
        currency=str(paymentin.amount.currency.code),
        description=paymentin.description,
        auto_capture=True,
        return_url=seccess_url,
    )

    paymentin.payment_gateway = YANDEX_KASSA_PAYMENT_GATEWAY
    paymentin.gateway_payment_id = yk_payment.id
    payment_url = yk_payment.confirmation.confirmation_url
    paymentin.gateway_payment_url = payment_url
    paymentin.save()

    return payment_url

_YK_STATUS_MAPPING = {
    'waiting_for_capture': PaymentIn.State.PROCESSED,
    'succeeded': PaymentIn.State.PROCESSED,
    'pending': PaymentIn.State.WAITING,
    'canceled': PaymentIn.State.CANCELLED,
}

def _yandex_kassa_update_payment_in_info(paymentin: PaymentIn, yk_payment: PaymentResponse):
    """
    Update state of the payment_in. Can raise AssertError of wrong input parameters.
    It *saves* the payment_in at the end of the method.

    :param paymentin:
    :param yk_payment:
    :return:
    """
    assert paymentin.payment_gateway == YANDEX_KASSA_PAYMENT_GATEWAY, \
        f'Wrong payment_gateway "{paymentin.payment_gateway}" for PaymentIn {paymentin}'
    mapped_status = _YK_STATUS_MAPPING.get(yk_payment.status)
    assert mapped_status, \
        f'Cannot map status {yk_payment.status} for {yk_payment}'

    yk_amount = float(yk_payment.amount.value)
    yk_currency = yk_payment.amount.currency
    paymentin_amount = float(paymentin.amount.amount)
    paymentin_currency = paymentin.amount.currency.code
    if yk_amount != paymentin_amount:
        logger.error(f'Incorrect amount {paymentin_amount} in PaymentIn. Correcting it to {yk_amount}')
        paymentin.amount = Money(yk_amount, yk_currency)
    if yk_currency != paymentin_currency:
        logger.error(f'Incorrect currency {paymentin_currency} in PaymentIn. Correcting it to {yk_currency}')
        paymentin.amount = Money(yk_amount, yk_currency)

    if paymentin.state != mapped_status:
        paymentin.state = mapped_status
        if mapped_status == PaymentIn.State.PROCESSED:
            paymentin.completed_at = timezone.now()

    paymentin.save()


def update_status_yandex_payments(days=3):
    """Update recent payments and update PaymentIn statuses."""
    yk_payments = yandex_kassa.list_recent_payments(duration=datetime.timedelta(days=days))
    for yk_payment in yk_payments:
        payment_id = yk_payment.id
        assert payment_id

        payment_in: PaymentIn = PaymentIn.objects.filter(gateway_payment_id=payment_id).first()
        if not payment_in:
            logger.warning(f'Cannot find PaymentIn for yandex kassa payment {payment_id}')
            continue

        logger.info(f'Processing yandex kassa payment {payment_id}, PaymentIn={payment_in}')
        try:
            _yandex_kassa_update_payment_in_info(payment_in, yk_payment)
        except AssertionError as e:
            logging.exception(e)


def run_periodic():
    update_status_yandex_payments()


def _yandex_kassa_update_payment_status(payment_in: PaymentIn):
    assert payment_in.payment_gateway == YANDEX_KASSA_PAYMENT_GATEWAY
    assert payment_in.gateway_payment_id, f"Shall have gateway_payment_id for {payment_in}"
    yk_payment = yandex_kassa.get_payment_by_id(payment_in.gateway_payment_id)
    _yandex_kassa_update_payment_in_info(payment_in, yk_payment)


def update_payment_status(payment_in):
    """
    Try to get latest information about the payment.

    :param payment_in: payment to update info
    :return: None
    """
    if payment_in.payment_gateway == YANDEX_KASSA_PAYMENT_GATEWAY:
        _yandex_kassa_update_payment_status(payment_in)
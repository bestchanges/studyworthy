import datetime
import logging

from django.utils import timezone
from djmoney.money import Money
from yandex_checkout import PaymentResponse

from djangoapps.crm.api import yandex_kassa
from djangoapps.erp.models import Payment

YANDEX_KASSA_PAYMENT_GATEWAY = 'yandex-kassa'

logger = logging.getLogger(__name__)


def pay_by_yandex_kassa(payment: Payment, seccess_url):
    """
    Create Payment object for Yandex Kassa for given Payment and save it's status
    After this call the user should be directed to returned URL.
    Note: payment_in object will be saved.

    :param payment: Not yet payed, positive amount, with empty payment_gateway Payment
    :param seccess_url: Full URL to which user shall be redirected after payment.
    :return: payment URL
    """
    assert payment.payment_gateway in (None, '', YANDEX_KASSA_PAYMENT_GATEWAY), \
        f"Payment gateway '{payment.payment_gateway}' not applicable for {payment}"
    assert payment.amount and payment.amount.amount > 0, \
        f"Inappropriate amount {payment.amount} for {payment}"
    assert payment.state in [Payment.State.WAITING, Payment.State.NEW], \
        f"Inappropriate state {payment.state} for {payment}"
    assert not payment.gateway_payment_id, \
        f"Yandex payment {payment.gateway_payment_id} is already created for {payment}"

    yk_payment = yandex_kassa.create_payment(
        amount=str(payment.amount.amount),
        currency=str(payment.amount.currency.code),
        description=payment.description,
        auto_capture=True,
        return_url=seccess_url,
    )

    payment.payment_gateway = YANDEX_KASSA_PAYMENT_GATEWAY
    payment.gateway_payment_id = yk_payment.id
    payment_url = yk_payment.confirmation.confirmation_url
    payment.gateway_payment_url = payment_url
    payment.save()

    return payment_url

_YK_STATUS_MAPPING = {
    'waiting_for_capture': Payment.State.PROCESSED,
    'succeeded': Payment.State.PROCESSED,
    'pending': Payment.State.WAITING,
    'canceled': Payment.State.CANCELLED,
}

def _yandex_kassa_update_payment_in_info(payment: Payment, yk_payment: PaymentResponse):
    """
    Update state of the payment_in. Can raise AssertError of wrong input parameters.
    It *saves* the payment_in at the end of the method.

    :param payment:
    :param yk_payment:
    :return:
    """
    assert payment.payment_gateway == YANDEX_KASSA_PAYMENT_GATEWAY, \
        f'Wrong payment_gateway "{payment.payment_gateway}" for Payment {payment}'
    mapped_status = _YK_STATUS_MAPPING.get(yk_payment.status)
    assert mapped_status, \
        f'Cannot map status {yk_payment.status} for {yk_payment}'

    yk_amount = float(yk_payment.amount.value)
    yk_currency = yk_payment.amount.currency
    payment_amount = float(payment.amount.amount)
    payment_currency = payment.amount.currency.code
    if yk_amount != payment_amount:
        logger.error(f'Incorrect amount {payment_amount} in Payment. Correcting it to {yk_amount}')
        payment.amount = Money(yk_amount, yk_currency)
    if yk_currency != payment_currency:
        logger.error(f'Incorrect currency {payment_currency} in Payment. Correcting it to {yk_currency}')
        payment.amount = Money(yk_amount, yk_currency)

    if payment.state != mapped_status:
        payment.state = mapped_status
        if mapped_status == Payment.State.PROCESSED:
            payment.completed_at = timezone.now()

    payment.save()


def update_status_yandex_payments(days=3):
    """Update recent payments and update Payment statuses."""
    yk_payments = yandex_kassa.list_recent_payments(duration=datetime.timedelta(days=days))
    for yk_payment in yk_payments:
        payment_id = yk_payment.id
        assert payment_id

        payment_in: Payment = Payment.objects.filter(gateway_payment_id=payment_id).first()
        if not payment_in:
            logger.warning(f'Cannot find Payment for yandex kassa payment {payment_id}')
            continue

        logger.info(f'Processing yandex kassa payment {payment_id}, Payment={payment_in}')
        try:
            _yandex_kassa_update_payment_in_info(payment_in, yk_payment)
        except AssertionError as e:
            logging.exception(e)


def run_periodic():
    update_status_yandex_payments()


def _yandex_kassa_update_payment_status(payment_in: Payment):
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
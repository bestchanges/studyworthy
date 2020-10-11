import datetime
import logging

from django.urls import reverse
from djmoney.money import Money
from yandex_checkout import PaymentResponse

from djangoapps.erp.models import Payment, Invoice, Organization
from . import api, config
from .config import GATEWAY_CODE, GATEWAY_NAME
from ..crm.logic.payments import PaymentGateway
from ..utils import build_full_url

logger = logging.getLogger(__name__)

_YANDEX_KASSA_ORGANIZATION = None


def _get_organization():
    global _YANDEX_KASSA_ORGANIZATION
    if not _YANDEX_KASSA_ORGANIZATION:
        _YANDEX_KASSA_ORGANIZATION = Organization.objects.get(code=config.ORGANIZATION_CODE)
    return _YANDEX_KASSA_ORGANIZATION


class YandexKassa(PaymentGateway):
    name = GATEWAY_NAME
    code = GATEWAY_CODE

    @classmethod
    def assert_can_pay_invocie(cls, invoice: Invoice) -> None:
        _assert_valid_invoice(invoice)

    @classmethod
    def pay_invoice(cls, invoice):
        payment = _create_payment(invoice)
        return _register_payment(payment)


def _assert_valid_invoice(invoice: Invoice) -> None:
    assert invoice.amount and invoice.amount.amount > 0, \
        f"Inappropriate amount {invoice.amount} for {invoice}"
    assert invoice.state in [Invoice.State.WAITING, Invoice.State.NEW], \
        f"Inappropriate state {invoice.state} for {invoice}"


def _create_payment(invoice):
    _assert_valid_invoice(invoice)
    payment = invoice.create_payment()
    payment.receiver_account = _get_organization().get_or_create_account(
        currency=invoice.amount.currency.code,
        account_name='external',
        description='Внешний аккаунт пользователя',
    )
    payment.sender_account = invoice.buyer.get_or_create_account(
        currency=invoice.amount.currency.code
    )
    payment.description = f'Оплата по счету {invoice.document_number} от {invoice.document_date}'
    payment.save()
    payment.set_state(Payment.State.NEW)
    return payment


def _register_payment(payment: Payment, success_url=None):
    """
    Create payment object for Yandex Kassa for given Payment and save it's status
    After this call the user should be directed to returned URL.
    Note: payment_in object will be saved.

    :param payment: Not yet payed, positive amount, with empty payment_gateway Payment
    :param success_url: Full URL to which user shall be redirected after payment.
    :return: payment URL
    """
    _assert_payment_can_be_payed(payment)
    if not success_url:
        path = reverse('yandex_kassa:payment_status', args=[payment.uuid])
        success_url = build_full_url(path)
    yk_payment = api.create_payment(
        amount=str(payment.amount.amount),
        currency=str(payment.amount.currency.code),
        description=payment.description,
        auto_capture=True,
        return_url=success_url,
        idempotence_key=str(payment.uuid),
    )

    payment.payment_gateway = config.PAYMENT_PROVIDER_CODE
    payment.gateway_payment_id = yk_payment.id
    payment_url = yk_payment.confirmation.confirmation_url
    payment.gateway_payment_url = payment_url
    payment.save()

    return payment_url


def _assert_payment_is_yandex_kassa(payment):
    """
    Check that payment has correct properties to be processed by Yandex Kassa.
    It doesn't check state of the payment.

    :param payment:
    :return:
    """
    assert payment.payment_gateway == config.PAYMENT_PROVIDER_CODE, \
        f"Payment gateway '{payment.payment_gateway}' not applicable for {payment}"
    assert payment.amount and payment.amount.amount > 0, \
        f"Inappropriate amount {payment.amount} for {payment}"
    assert payment.gateway_payment_id, f"Shall have gateway_payment_id for {payment}"


def _assert_payment_can_be_payed(payment):
    """
    Check that payment has correct properties to be processed by Yandex Kassa.
    It doesn't check state of the payment.

    :param payment:
    :return:
    """
    assert payment.payment_gateway in (None, '', config.PAYMENT_PROVIDER_CODE), \
        f"Payment gateway '{payment.payment_gateway}' not applicable for {payment}"
    assert payment.amount and payment.amount.amount > 0, \
        f"Inappropriate amount {payment.amount} for {payment}"
    assert payment.state in [Payment.State.WAITING, Payment.State.NEW], \
        f"Inappropriate state {payment.state} for {payment}"
    assert not payment.gateway_payment_id, \
        f"Yandex payment {payment.gateway_payment_id} is already created for {payment}"


_YK_STATUS_MAPPING = {
    'waiting_for_capture': Payment.State.PROCESSED,
    'succeeded': Payment.State.PROCESSED,
    'pending': Payment.State.WAITING,
    'canceled': Payment.State.CANCELLED,
}


def _update_payment_status(payment: Payment, yk_payment: PaymentResponse):
    """
    Update state of the payment. Can raise AssertError of wrong input parameters.
    It *saves* the payment at the end of the method.

    :param payment:
    :param yk_payment:
    :return:
    """
    _assert_payment_is_yandex_kassa(payment)

    mapped_status = _YK_STATUS_MAPPING.get(yk_payment.status)
    assert mapped_status, \
        f'Cannot map status {yk_payment.status} for {yk_payment}'

    # float because of https://github.com/yandex-money/yandex-checkout-sdk-python/pull/64
    yk_amount = float(yk_payment.amount.value)
    yk_currency = yk_payment.amount.currency
    payment_amount = float(payment.amount.amount)
    payment_currency = payment.amount.currency.code

    # Let's find out if there are some updates
    need_save = False
    if yk_amount != payment_amount:
        logger.error(f'Incorrect amount {payment_amount} in Payment. Correcting it to {yk_amount}')
        payment.amount = Money(yk_amount, yk_currency)
        need_save = True
    if yk_currency != payment_currency:
        logger.error(f'Incorrect currency {payment_currency} in Payment. Correcting it to {yk_currency}')
        payment.amount = Money(yk_amount, yk_currency)
        need_save = True

    if payment.state != mapped_status:
        payment.state = mapped_status
        need_save = True

    if need_save:
        logger.info(f'Updating payment {payment}')
        payment.save()
    else:
        logger.debug(f'No need to update {payment}')


def update_payment_status(payment):
    """
    Try to get latest information about the payment.

    :param payment: payment to update info
    :return: None
    """
    _assert_payment_is_yandex_kassa(payment)
    yk_payment = api.get_payment_by_id(payment.gateway_payment_id)
    _update_payment_status(payment, yk_payment)


def update_status_yandex_payments(days):
    """Update recent payments and update Payment statuses."""
    yk_payments = api.list_recent_payments(duration=datetime.timedelta(days=days))
    for yk_payment in yk_payments:
        payment_id = yk_payment.id
        assert payment_id

        payment_in: Payment = Payment.objects.filter(gateway_payment_id=payment_id).first()
        if not payment_in:
            logger.warning(f'Cannot find Payment for yandex kassa payment {payment_id}')
            continue

        logger.info(f'Processing yandex kassa payment {payment_id}, Payment={payment_in}')
        try:
            _update_payment_status(payment_in, yk_payment)
        except AssertionError as e:
            logging.exception(e)

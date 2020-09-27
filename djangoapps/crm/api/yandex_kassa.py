import datetime
import logging
import os

import uuid
import yandex_checkout

logger = logging.getLogger(__name__)


def init():
    api_key = os.environ.get('YANDEX_KASSA_API_KEY')
    shop_id = os.environ.get('YANDEX_KASSA_SHOP_ID')
    if api_key and shop_id:
        yandex_checkout.Configuration.configure(shop_id, api_key)
        logger.info(f'Yandex kassa configured. YANDEX_KASSA_SHOP_ID={shop_id}')
    else:
        logger.warning('Yandex kassa not configured. Set YANDEX_KASSA_API_KEY and YANDEX_KASSA_SHOP_ID in env.')


def create_payment(amount, currency, description, return_url, auto_capture: bool = True):
    assert amount
    assert currency
    assert description
    assert return_url
    idempotence_key = str(uuid.uuid4())
    yandex_payment = yandex_checkout.Payment.create({
        "amount": {
            "value": amount,
            "currency": currency,
        },
        # "payment_method_data": {
        #     "type": "bank_card"
        # },
        "capture": auto_capture,
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "description": description
    }, idempotence_key)

    return yandex_payment


def list_recent_payments(duration: datetime.timedelta = None):
    if not duration:
        duration = datetime.timedelta(days=1)

    now = datetime.datetime.today()
    period_start = now - duration
    # https://kassa.yandex.ru/developers/api?lang=python#get_payments_list
    params = {
        "created_at.gte": period_start.isoformat()
    }
    response = yandex_checkout.Payment.list(params)
    if 'next_cursor' in response:
        logger.warning(f'Returned partial list. Which is NOT supported yet. Some data will not be processed')
    return response.items
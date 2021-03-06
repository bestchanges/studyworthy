import logging

import responses
from django.test import TestCase
from django.urls import reverse
from djmoney.money import Money

from djangoapps.crm.logic import payments
from djangoapps.erp.models import Person, Invoice, Organization
from . import config

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

import http.client

httpclient_logger = logging.getLogger("http.client")


def httpclient_logging_patch(level=logging.DEBUG):
    """Enable HTTPConnection debug logging to the logging framework"""

    def httpclient_log(*args):
        httpclient_logger.log(level, " ".join(args))

    # mask the print() built-in in the http.client module to use
    # logging instead
    http.client.print = httpclient_log
    # enable debugging
    http.client.HTTPConnection.debuglevel = 1


http.client.HTTPConnection.debuglevel = 1


def test_register_as_payment_gateway_in_crm(self):
    gateway = payments.get_gateway(config.GATEWAY_CODE)

    self.assertEqual(gateway.name, config.GATEWAY_NAME)


class MyTestCase(TestCase):
    def setUp(self) -> None:
        from . import app_init
        app_init.init()
        self.currency = 'RUB'
        self.seller = Organization.objects.create()
        self.buyer = Person.objects.create()
        self.invoice = Invoice.objects.create(
            seller=self.seller,
            buyer=self.buyer,
            amount=Money(10, self.currency)
        )
        self.invoice.set_state(Invoice.State.NEW)

    @responses.activate
    def test_invoice_payment(self):
        response_body = {
            'id': '27104eed-000f-5000-a000-147e8c46cebe',
            'status': 'pending',
            'paid': False,
            'amount': {'value': '10.00', 'currency': 'RUB'},
            'confirmation': {
                'type': 'redirect',
                'confirmation_url': 'https://money.yandex.ru/api-pages/v2/payment-confirm/epl?orderId=27104eed-000f-5000-a000-147e8c46cebe'
            },
            'created_at': '2020-10-07T22:03:25.852Z',
            'description': 'Оплата по счету I-1 от 2020-10-07',
            'metadata': {'scid': '1695491'},
            'recipient': {'account_id': '632492', 'gateway_id': '1613193'},
            'refundable': False,
            'test': False}
        responses.add(responses.POST, 'https://payment.yandex.net/api/v3/payments',
                      json=response_body, status=200)

        path = reverse('yandex_kassa:invoice_payment', args=[str(self.invoice.uuid)])
        response = self.client.get(path)
        self.assertEqual(302, response.status_code)
        expected_redirect = 'https://money.yandex.ru/api-pages/v2/payment-confirm/epl?orderId=27104eed-000f-5000-a000-147e8c46cebe'
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)
        # TODO: check created and updated models


    def test_invoice_update(self):
        # before update we need to register the payment
        assert self.invoice.payments.count() == 0
        self.test_invoice_payment()
        assert self.invoice.payments.count() == 1
        payment = self.invoice.payments.first()

        response_body = {
            'id': '27104eed-000f-5000-a000-147e8c46cebe',
            'status': 'pending',
            'paid': False,
            'amount': {'value': '10.00', 'currency': 'RUB'},
            'confirmation': {
                'type': 'redirect',
                'confirmation_url': 'https://money.yandex.ru/api-pages/v2/payment-confirm/epl?orderId=27104eed-000f-5000-a000-147e8c46cebe'
            },
            'created_at': '2020-10-07T22:03:25.852Z',
            'description': 'Оплата по счету I-1 от 2020-10-07',
            'metadata': {'scid': '1695491'},
            'recipient': {'account_id': '632492', 'gateway_id': '1613193'},
            'refundable': False,
            'test': False}
        responses.add(responses.POST, 'https://payment.yandex.net/api/v3/payments',
                      json=response_body, status=200)

        path = reverse('yandex_kassa:payment_status', args=[str(payment.uuid)])
        response = self.client.get(path)

        self.assertEqual(200, response.status_code)
        # TODO: check models

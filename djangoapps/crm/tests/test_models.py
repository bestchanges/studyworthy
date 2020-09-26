import datetime

from django.test import TestCase
from django.utils import timezone
from djmoney.money import Money

from djangoapps.crm.models.erp_models import Invoice, PaymentIn, Shipment, Product, ClientOrder
from djangoapps.lms.models.base import Person


class TestModels(TestCase):

    def setUp(self):
        self.product_1, self.product_2 = self._create_products()

    def tearDown(self):
        self.product_1.delete()
        self.product_2.delete()

    def test_document_number(self):
        order = ClientOrder()
        order.save()
        self.assertEquals("CO-1", order.document_number)

        order_2 = ClientOrder()
        order_2.save()
        self.assertEquals("CO-2", order_2.document_number)

        invoice = order.create_invoice()
        invoice.save()
        self.assertEquals("I-1", invoice.document_number)

        invoice_2 = order.create_invoice()
        invoice_2.save()
        self.assertEquals("I-2", invoice_2.document_number)

        # create invoice one month later
        self.assertTrue('{number_month}' in Invoice.document_number_template,
                        "Invoices suppose to be month-dependant")
        invoice_3 = order.create_invoice()
        invoice_3.created_at = timezone.now() + datetime.timedelta(days=31)
        invoice_3.save()
        self.assertEquals("I-1", invoice_3.document_number)

    def test_client_order(self):
        buyer = Person()
        buyer.save()
        order = ClientOrder(client=buyer, currency='RUB')
        order.save()
        order.add_item(self.product_1, 2)
        order.add_item(self.product_2, 1)

        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.amount, Money(35, 'RUB'))

    def test_payment_in(self):
        buyer = Person()
        buyer.save()
        amount = Money(10, 'RUB')
        payment = PaymentIn(payer=buyer, amount=amount)
        payment.save()

        self.assertTrue(payment.is_applicable)
        self.assertEqual(payment.amount, amount)

    def test_invoice_and_payment(self):
        product_1, product_2 = self._create_products()

        buyer = Person()
        buyer.save()
        invoice = Invoice(code='Invoice-1', buyer=buyer, currency='RUB')
        invoice.save()
        invoice.add_item(product_1, 2)
        invoice.add_item(product_2, 1)

        amount_1 = Money(10, 'RUB')
        payment_1 = PaymentIn(code='p1', payer=buyer, amount=amount_1, invoice=invoice)
        payment_1.save()

        self.assertEqual(invoice.payed_amount, amount_1)
        self.assertFalse(invoice.is_payed)

        amount_2 = Money(7, 'RUB')
        payment_2 = PaymentIn(code='p2', payer=buyer, amount=amount_2, invoice=invoice)
        payment_2.save()

        self.assertEqual(invoice.payed_amount, amount_1 + amount_2)
        self.assertFalse(invoice.is_payed)

        amount_3 = Money(18, 'RUB')
        payment_3 = PaymentIn(code='p3', payer=buyer, amount=amount_3, invoice=invoice)
        payment_3.save()

        self.assertEqual(invoice.payed_amount, amount_1 + amount_2 + amount_3)
        self.assertTrue(invoice.is_payed)

    def test_shipment(self):
        product_1, product_2 = self._create_products()

        buyer = Person()
        buyer.save()
        shipment = Shipment(receiver=buyer)
        shipment.save()
        shipment.add_item(product_1, 2)
        shipment.add_item(product_2, 1)

        self.assertEqual(shipment.shipmentitem_set.count(), 2)

    def _create_products(self):
        Product(name='test product 1', price=Money(10, 'RUB'))
        product_1 = Product(code='product-1', name='test product 1', price=Money(10, 'RUB'))
        product_1.save()
        product_2 = Product(code='product-2', name='test product 2', price=Money(15, 'RUB'))
        product_2.save()
        return product_1, product_2



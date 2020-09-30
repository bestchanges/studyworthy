import datetime

from django.test import TestCase
from django.utils import timezone
from djmoney.money import Money

from djangoapps.erp.models import Person, Product, ClientOrder, Invoice, \
    PaymentIn


class TestModels(TestCase):

    def setUp(self):
        self._delete_products()
        self.product_1, self.product_2 = self._create_products()

    def tearDown(self):
        self._delete_products()

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
        self.assertTrue('{number_month}' in Invoice.DOCUMENT_NUMBER_TEMPLATE,
                        "Invoices suppose to be month-dependant")
        invoice_3 = order.create_invoice()
        invoice_3.document_date = timezone.now().date() + datetime.timedelta(days=31)
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

    def test_client_order_state_update(self):
        """Upon ivoice getting paid the order start processing """
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

        self.assertEqual(payment.amount, amount)

    def test_invoice_and_payment(self):
        """
        1. Create ClientOrder -> Invoice -> PaymentIn
        2. When Payment is payed -> Invoice state shall be updated
        :return:
        """
        order = ClientOrder()
        order.save()
        order.add_item(self.product_1, 2)
        order.add_item(self.product_2, 1)
        amount = self.product_1.price * 2 + self.product_2.price
        self.assertEqual(order.amount, amount)

        invoice = order.create_invoice()
        invoice.save()
        self.assertEqual(order.amount, invoice.amount)
        self.assertEqual(order, invoice.client_order)
        self.assertIsNone(invoice.state)

        payment_in = invoice.create_payment()
        payment_in.state = PaymentIn.State.WAITING
        payment_in.save()
        self.assertEqual(invoice.amount, payment_in.amount)
        # after create paymentIn the signal should update invoice state
        # invoice = Invoice.objects.get(pk=invoice.pk)
        self.assertEqual(invoice.state, invoice.State.WAITING)
        self.assertEqual(invoice, payment_in.invoice)
        self.assertFalse(payment_in.is_completed())

        payment_in.set_state(payment_in.State.PROCESSED)
        self.assertEqual(payment_in.state, payment_in.State.PROCESSED)
        self.assertTrue(payment_in.is_completed())
        # invoice should respect payment_in state change
        self.assertEqual(invoice.state, invoice.State.PAYED_FULLY)

    def test_invoice_partial_payment(self):
        invoice = Invoice(
            amount=Money(25, 'RUB')
        )
        invoice.save()
        self.assertIsNone(invoice.state)
        self.assertFalse(invoice.is_payed)

        amount_1 = Money(18, 'RUB')

        amount_2 = Money(7, 'RUB')
        payment_2 = PaymentIn(amount=amount_2, invoice=invoice)
        payment_2.save()

        # waiting state doesn't change anything
        payment_2.set_state(payment_2.State.WAITING)
        self.assertEqual(invoice.state, invoice.State.WAITING)
        self.assertFalse(invoice.is_payed)

        # partly payed invoice
        payment_2.set_state(PaymentIn.State.PROCESSED)
        self.assertEqual(invoice.state, Invoice.State.PAYED_PARTLY)
        self.assertFalse(invoice.is_payed)

        payment_1 = PaymentIn(amount=amount_1, invoice=invoice)
        payment_1.save()
        # newly created payment has not processed yet, so no state change
        self.assertEqual(invoice.state, invoice.State.PAYED_PARTLY)
        self.assertFalse(invoice.is_payed)

        # fully payed invoice
        payment_1.set_state(PaymentIn.State.PROCESSED)
        self.assertEqual(invoice.state, invoice.State.PAYED_FULLY)
        self.assertTrue(invoice.is_payed)

    def test__guess_first_and_last_name(self):
        self.assertEqual(Person._guess_first_and_last_name('John Deer'), ('John', 'Deer'))
        self.assertEqual(Person._guess_first_and_last_name('John'), ('John', ''))
        self.assertEqual(Person._guess_first_and_last_name('John '), ('John', ''))
        self.assertEqual(Person._guess_first_and_last_name(' John '), ('John', ''))
        self.assertEqual(Person._guess_first_and_last_name('John Somer Deer'), ('John', 'Somer Deer'))
        self.assertEqual(Person._guess_first_and_last_name('John   Somer '), ('John', 'Somer'))
        self.assertEqual(Person._guess_first_and_last_name(None), ('', ''))

    def _create_products(self):
        Product(name='test product 1', price=Money(10, 'RUB'))
        product_1 = Product(code='product-1', name='test product 1', price=Money(10, 'RUB'))
        product_1.save()
        product_2 = Product(code='product-2', name='test product 2', price=Money(15, 'RUB'))
        product_2.save()
        return product_1, product_2

    def _delete_products(self):
        Product.objects.filter(code__in=['product-1', 'product-2']).delete()



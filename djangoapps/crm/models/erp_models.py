from functools import reduce

from django.db import models
from djmoney.models.fields import MoneyField
from django.conf import settings
from djmoney.money import Money

from lms.models.base import CodeNaturalKeyAbstractModel, Person


class Product(CodeNaturalKeyAbstractModel):
    class State(models.TextChoices):
        DRAFT = 'draft'
        ACTIVE = 'active'
        ARCHIVED = 'archived'

    price = MoneyField(max_digits=14, decimal_places=2, default_currency=settings.BASE_CURRENCY)
    name = models.CharField(max_length=250)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = MoneyField(max_digits=14, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def sum(self):
        return self.price * self.quantity


class Invoice(CodeNaturalKeyAbstractModel):
    is_applicable = models.BooleanField(default=True)
    buyer = models.ForeignKey(Person, on_delete=models.PROTECT)
    items = models.ManyToManyField(Product, through=InvoiceItem)
    currency = models.CharField(max_length=10, default=settings.BASE_CURRENCY)
    valid_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    @property
    def amount(self):
        currency = self.currency
        if not currency:
            raise ValueError(f'No currency in order {self}')
        return reduce(lambda x, item: x + item.sum, self.invoiceitem_set.all(), Money(0, currency))

    @property
    def payed_amount(self):
        return reduce(lambda x, payment: x + payment.amount, self.paymentin_set.all(), Money(0, self.currency))

    @property
    def is_payed(self):
        return self.amount == self.payed_amount

    def add_item(self, product: Product, quantity: int):
        item = InvoiceItem(product=product, invoice=self, quantity=quantity, price=product.price)
        item.save()
        self.invoiceitem_set.add(item)


class PaymentIn(CodeNaturalKeyAbstractModel):
    is_applicable = models.BooleanField(default=True)
    payer = models.ForeignKey(Person, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    amount = MoneyField(max_digits=14, decimal_places=2, default_currency=settings.BASE_CURRENCY)
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Shipment(CodeNaturalKeyAbstractModel):
    is_applicable = models.BooleanField(default=True)
    receiver = models.ForeignKey(Person, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Product, through=ShipmentItem)
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)

    def add_item(self, product: Product, quantity: int):
        item = ShipmentItem(product=product, shipment=self, quantity=quantity)
        item.save()
        self.shipmentitem_set.add(item)

    @staticmethod
    def from_invoice(invoice: Invoice):
        shipment = Shipment(invoice=invoice, receiver=invoice.buyer)
        for invoice_item in invoice.invoiceitem_set.all():
            shipment.add_item(invoice_item.product, invoice_item.quantity)
        return shipment

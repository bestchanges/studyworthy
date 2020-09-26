import datetime
from functools import reduce

import uuid
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField, CurrencyField
from djmoney.money import Money

from djangoapps.lms.models.base import CodeNaturalKeyAbstractModel, Person


class Product(CodeNaturalKeyAbstractModel):
    class State(models.TextChoices):
        DRAFT = 'draft'
        ACTIVE = 'active'
        ARCHIVED = 'archived'

    price = MoneyField(max_digits=14, decimal_places=2)
    name = models.CharField(max_length=250)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


class Document(models.Model):
    document_number_template = 'D-{number_total}'
    document_number = models.CharField(max_length=200, blank=True, null=True)
    document_date = models.DateField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # document_applicable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_create = self.pk is None
        if is_create and not self.document_number:
            template = self.document_number_template
            if not self.document_date:
                self.document_date = timezone.now().date()
            today_start = self.document_date
            month_start = today_start.replace(day=1)
            year_start = month_start.replace(month=1)
            number = template.format(
                number_today = self.__class__.objects.filter(document_date__gte=today_start).count() + 1,
                number_month = self.__class__.objects.filter(document_date__gte=month_start).count() + 1,
                number_year = self.__class__.objects.filter(document_date__gte=year_start).count() + 1,
                number_total = self.__class__.objects.all().count() + 1,
            )
            self.document_number = number
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True


class ClientOrder(Document):
    document_number_template = 'CO-{number_month}'

    class State(models.TextChoices):
        NEW = 'new'
        WAITING = 'waiting'
        COMPLETED = 'completed'
        CANCELLED = 'cancelled'

    client = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    currency = CurrencyField()
    valid_until = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)

    client_name = models.CharField(max_length=200, null=True, blank=True)
    client_email = models.EmailField(null=True, blank=True)
    client_phone = models.CharField(max_length=200, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    @property
    def amount(self):
        currency = self.currency
        if not currency:
            raise ValueError(f'No currency in order {self}')
        return reduce(lambda x, item: x + item.sum, self.items.all(), Money(0, currency))

    def add_item(self, product: Product, quantity: int = 1):
        ClientOrderItem.objects.create(
            product=product,
            client_order=self,
            price=product.price,
            quantity=quantity
        )

    def create_invoice(self):
        return Invoice(
            client_order=self,
            amount=self.amount,
            client=self.client,
        )


class ClientOrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    client_order = models.ForeignKey(ClientOrder, on_delete=models.CASCADE, related_name='items')
    price = MoneyField(max_digits=14, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def sum(self):
        return self.price * self.quantity


class Invoice(Document):
    document_number_template = 'I-{number_month}'

    class State(models.TextChoices):
        NEW = 'new'
        PAYED_PARTLY = 'payed_partly'
        PAYED_FULLY = 'payed_fully'
        CANCELLED = 'cancelled'

    client = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)

    client_order = models.ForeignKey(ClientOrder, on_delete=models.PROTECT, null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    amount = MoneyField(max_digits=14, decimal_places=2)

    @property
    def payed_amount(self):
        # TODO: filter payments by state
        return reduce(lambda x, payment: x + payment.amount, self.paymentin_set.all(), Money(0, self.amount.default_currency))

    @property
    def is_payed(self):
        return self.payed_amount >= self.amount


class PaymentGateway(CodeNaturalKeyAbstractModel):
    name = models.CharField(max_length=250)


class PaymentIn(Document):
    document_number_template = 'PI-{number_year}'

    gateway = models.ForeignKey(PaymentGateway, null=True, blank=True, help_text="Payment gateway", on_delete=models.PROTECT)
    gateway_payment_id = models.CharField(max_length=255, null=True, blank=True, help_text="Payment ID in the gateway")
    gateway_payment_url = models.URLField(null=True, blank=True, help_text="URL to pay this payment")
    payer = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    amount = MoneyField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def is_completed(self):
        return bool(self.completed_at)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Shipment(Document):
    document_number_template = 'S-{number_year}'

    receiver = models.ForeignKey(Person, on_delete=models.PROTECT)
    order = models.ForeignKey(ClientOrder, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Product, through=ShipmentItem)
    description = models.CharField(max_length=255, null=True, blank=True)

    def add_item(self, product: Product, quantity: int):
        item = ShipmentItem(product=product, shipment=self, quantity=quantity)
        item.save()
        self.shipmentitem_set.add(item)

    @staticmethod
    def from_order(order: ClientOrder):
        shipment = Shipment(order=order, receiver=order.client)
        for item in order.items.all():
            shipment.add_item(item.product, item.quantity)
        return shipment

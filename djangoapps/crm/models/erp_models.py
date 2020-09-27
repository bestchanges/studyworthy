from functools import reduce

from django.db import models
from djmoney.models.fields import MoneyField, CurrencyField
from djmoney.money import Money

from djangoapps.common.models import Document
from djangoapps.lms.models.base import CodeNaturalKeyAbstractModel, Person


class Product(CodeNaturalKeyAbstractModel):
    class State(models.TextChoices):
        DRAFT = 'DRAFT', 'Черновик'
        ACTIVE = 'ACTIVE', 'Активен'
        ARCHIVED = 'ARCHIVED', 'Архивирован'

    price = MoneyField(max_digits=14, decimal_places=2)
    name = models.CharField(max_length=250)
    state = models.CharField(max_length=8, choices=State.choices, default=State.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, editable=False)


class ClientOrder(Document):
    document_number_template = 'CO-{number_month}'

    class State(models.TextChoices):
        NEW = 'NEW', "Новый"
        WAITING = 'WAITING', "Ожидает"
        COMPLETED = 'COMPLETED', "Выполнен"
        PROCESSING = 'PROCESSING', "Исполняется"
        CANCELLED = 'CANCELLED', "Отменён"

    state = models.CharField(max_length=20, choices=State.choices, null=True, blank=True)
    client = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    currency = CurrencyField()
    valid_until = models.DateField(null=True, blank=True)

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

    def create_invoice(self) -> 'Invoice':
        return Invoice(
            client_order=self,
            amount=self.amount,
            client=self.client,
        )


class ClientOrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    client_order = models.ForeignKey(ClientOrder, on_delete=models.CASCADE, related_name='items')
    price = MoneyField(max_digits=14, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def sum(self):
        return self.price * self.quantity


class Invoice(Document):
    document_number_template = 'I-{number_month}'

    class State(models.TextChoices):
        NEW = 'NEW', 'Новый'
        WAITING = 'WAITING', 'Ожидает'
        PAYED_PARTLY = 'PAYED_PARTLY', 'Частично оплачен'
        PAYED_FULLY = 'PAYED_FULLY', 'Полностью оплачен'
        CANCELLED = 'CANCELLED', 'Отменен'

    client = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)

    client_order = models.ForeignKey(ClientOrder, on_delete=models.PROTECT, null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    amount = MoneyField(max_digits=14, decimal_places=2)

    @property
    def payed_amount(self):
        return reduce(
            lambda x, payment: x + payment.amount,
            self.paymentin_set.filter(state=PaymentIn.State.PROCESSED),
            Money(0, self.amount.currency))

    @property
    def is_payed(self):
        return self.payed_amount >= self.amount

    def create_payment(self) -> 'PaymentIn':
        if self.document_number and self.document_date:
            description = f"Оплата по счёту \"{self.document_number}\" от {self.document_date.strftime('%d.%m.%Y')}"
        else:
            description = ''
        return PaymentIn(
            invoice=self,
            amount=self.amount,
            payer=self.client,
            description=description
        )


class PaymentIn(Document):
    document_number_template = 'PI-{number_year}'

    class State(models.TextChoices):
        NEW = 'NEW', 'Новый'
        WAITING = 'WAITING', 'Ожидает оплаты'
        PROCESSED = 'PROCESSED', 'Получен'
        CANCELLED = 'CANCELLED', 'Отменен'

    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)

    payer = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    amount = MoneyField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)

    payment_gateway = models.CharField(max_length=255, null=True, blank=True, help_text="Payment gateway")
    gateway_payment_id = models.CharField(max_length=255, null=True, blank=True, help_text="Payment ID in the gateway")
    gateway_payment_url = models.URLField(null=True, blank=True, help_text="URL to pay this payment")
    completed_at = models.DateTimeField(null=True, blank=True)

    def is_completed(self):
        return self.state == self.State.PROCESSED

    def __str__(self):
        return f'#{self.id} {self.amount} ({self.state})'


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

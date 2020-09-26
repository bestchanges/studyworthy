from djangoapps.crm.api import yandex_kassa
from djangoapps.crm.models.erp_models import Invoice, PaymentIn


def create_yandex_payment_from_invoice(invoice: Invoice):
    description = f"Заказ #{invoice.document_number} от {invoice.document_date}"
    payment_in = PaymentIn.objects.create(
        payer=invoice.client,
        invoice=invoice,
        amount=invoice.amount,
        description=description
    )
    yandex_payment = yandex_kassa.create_payment(
        amount=str(payment_in.amount.amount),
        currency=str(payment_in.amount.currency.code),
        description=description,
        return_url="https://ya.ru",
    )

    payment_in.gateway_payment_id = yandex_payment.id
    # get confirmation url
    confirmation_url = yandex_payment.confirmation.confirmation_url
    payment_in.gateway_payment_url = confirmation_url
    payment_in.save()

    return payment_in

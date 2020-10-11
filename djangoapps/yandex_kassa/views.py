from django.shortcuts import redirect, render
from django.urls import reverse

from djangoapps.erp.models import Invoice, Payment
from djangoapps.yandex_kassa import logic
from djangoapps.yandex_kassa.logic import YandexKassa


def invoice_payment(request, invoice_uuid):
    invoice = Invoice.objects.get(uuid=invoice_uuid)
    payment_url = YandexKassa.pay_invoice(invoice)
    return redirect(payment_url)


def update_payment_status(request, payment_uuid):
    """
    Update payments status and redirect to payment status view

    :param request:
    :param uuid:
    :return: 302 redirect
    """
    payment = Payment.objects.get(uuid=payment_uuid)
    logic.update_payment_status(payment)
    context = {
        'payment': payment,
    }
    return render(request, 'yandex_kassa/payment_status.html', context)

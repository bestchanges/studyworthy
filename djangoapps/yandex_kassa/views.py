from django.shortcuts import redirect
from django.urls import reverse

from djangoapps.erp.models import Invoice, Payment
from djangoapps.yandex_kassa import logic
from djangoapps.yandex_kassa.logic import create_payment


def invoice_payment(request, invoice_uuid):
    invoice = Invoice.objects.get(uuid=invoice_uuid)

    payment = create_payment(invoice)
    payment.save()
    payment.set_state(Payment.State.NEW)

    next = reverse('crm:payment_status', args=[invoice.uuid])
    payment_url = logic.pay_by_yandex_kassa(
        payment=payment,
        seccess_url=next,
    )
    return redirect(payment_url)


def update_payment_status(request, invoice_uuid):
    """
    Update payments status and redirect to payment status view

    :param request:
    :param uuid:
    :return: 302 redirect
    """
    invoice = Invoice.objects.get(uuid=invoice_uuid)
    next = request.GET.get('next', reverse('crm:payment_status', args=[invoice.uuid]))
    for payment in invoice.payments.all():
        logic.update_payment_status(payment)
    return redirect(next)

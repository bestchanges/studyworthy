from django.shortcuts import render, redirect
from django.urls import reverse

from djangoapps.crm.forms import SingleCourseProductOrderForm
from djangoapps.crm.logic import payments
from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Order, Invoice, Payment


def index(request):
    courses = CourseProduct.objects.filter(state=CourseProduct.State.ACTIVE)
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)


def order_single_product(request):
    if request.method == "POST":
        form = SingleCourseProductOrderForm(request.POST)
        if form.is_valid():
            client_order: Order = form.create_order()
            client_order.set_state(Invoice.State.NEW)

            if client_order.amount.amount:
                invoice = client_order.create_invoice()
                invoice.set_state(Invoice.State.NEW)
                return redirect(reverse('crm:invoice_payment', args=[invoice.uuid]))
            else:
                return redirect(reverse('crm:order_accepted'))
    else:
        form = SingleCourseProductOrderForm()
    context = {
        'form': form,
    }
    return render(request, 'crm/order_form.html', context)


def order_accepted(request):
    return render(request, 'crm/order_accepted.html', {})


def invoice(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    context = {
        'invoice': invoice,
    }
    return render(request, 'crm/invoice_payment.html', context)


def invoice_payment(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    payment = invoice.create_payment()
    payment.set_state(Payment.State.NEW)
    payment_url = payments.pay_by_yandex_kassa(
        payment=payment,
        seccess_url=request.build_absolute_uri(reverse('crm:payment_status', args=[payment.uuid])),
    )
    return redirect(payment_url)


def payment_status(request, uuid):
    """
    Check payment status and display it to user.

    :param request:
    :param uuid:
    :return:
    """
    paymentin = Payment.objects.get(uuid=uuid)
    payments.update_payment_status(paymentin)
    context = {
        "paymentin": paymentin,
    }
    return render(request, 'crm/payment_status.html', context)

from djangoapps.crm.forms import ClientOrderForm
from djangoapps.crm.logic import payments
from djangoapps.crm.models.crm_models import CourseProduct
from djangoapps.crm.models.erp_models import ClientOrder, Invoice, PaymentIn
from django.shortcuts import render, redirect
from django.urls import reverse

from djangoapps.crm import logic


def index(request):
    courses = CourseProduct.objects.filter(state=CourseProduct.State.ACTIVE)
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)


def course_product(request, code):
    product = CourseProduct.objects.get(code=code)
    if request.method == "POST":
        form = ClientOrderForm(request.POST)
        if form.is_valid():
            client_order: ClientOrder = form.save(commit=False)
            client_order.product = product
            client_order.save()

            client_order.add_item(product, 1)

            # after added child object we can state NEW
            client_order.state = ClientOrder.State.NEW
            client_order.save()

            invoice = client_order.create_invoice()
            invoice.save()
            return redirect(reverse('crm:invoice_payment', args=[invoice.uuid]))
    else:
        form = ClientOrderForm()
    context = {
        'product': product,
        'course': product.items.all()[0],
        'form': form,
    }
    return render(request, 'crm/course_product.html', context)


def enrollment_accepted(request):
    return render(request, 'crm/enrollment_accepted.html', {})


def invoice(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    context = {
        'invoice': invoice,
    }
    return render(request, 'crm/invoice_payment.html', context)


def invoice_payment(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    paymentin = invoice.create_payment()
    payment_url = payments.pay_by_yandex_kassa(
        paymentin=paymentin,
        seccess_url=request.build_absolute_uri(reverse('crm:payment_status', args=[paymentin.uuid])),
    )
    return redirect(payment_url)


def payment_status(request, uuid):
    """
    Check payment status and display it to user.

    :param request:
    :param uuid:
    :return:
    """
    paymentin = PaymentIn.objects.get(uuid=uuid)
    payments.update_payment_status(paymentin)
    context = {
        "paymentin": paymentin,
    }
    return render(request, 'crm/payment_status.html', context)

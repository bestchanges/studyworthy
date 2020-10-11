from django.shortcuts import render, redirect
from django.urls import reverse

from djangoapps.crm.forms import SingleCourseProductOrderForm, OrderConfirmationForm
from djangoapps.erp.models import Order, Invoice, Payment


def order_single_product(request):
    if request.method == "POST":
        form = SingleCourseProductOrderForm(request.POST)
        if form.is_valid():
            client_order: Order = form.create_order()
            client_order.set_state(Invoice.State.NEW)

            if client_order.amount.amount:
                return redirect(reverse('crm:order-overview', args=[client_order.uuid]))
            else:
                # TODO: write form success_message from CourseProductCMSPluginConfig
                return redirect(reverse('order-accepted', args=[client_order.uuid]))
    else:
        form = SingleCourseProductOrderForm()
    context = {
        'form': form,
    }
    return render(request, 'crm/order_form.html', context)


def order_accepted(request, order_uuid):
    return render(request, 'crm/order_accepted.html', {})


def order_overview(request, order_uuid):
    order = Order.objects.get(uuid=order_uuid)
    if request.method == "POST":
        form = OrderConfirmationForm(order=order, data=request.POST)
        if form.is_valid():
            gateway = form.get_gateway()

            invoice = form.create_invoice()
            invoice.set_state(Invoice.State.NEW)
            invoice.save()

            redirect_url = gateway.pay_invoice(invoice)
            return redirect(redirect_url)
    else:
        form = OrderConfirmationForm(order=order)
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'crm/order_overview.html', context)


def order_pay(request, order_uuid):
    order = Order.objects.get(uuid=order_uuid)
    invoice = order.create_invoice()
    invoice.set_state(Invoice.State.NEW)
    context = {
        'order': order,
        'invoice': invoice,
    }
    return render(request, 'crm/order_overview.html', context)


def order_payment_view(request):
    return render(request, 'crm/order_accepted.html', {})


def invoice(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    context = {
        'invoice': invoice,
    }
    return render(request, 'crm/invoice_payment.html', context)

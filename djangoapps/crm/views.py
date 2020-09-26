from djangoapps.crm.forms import ClientOrderForm
from djangoapps.crm.models.crm_models import CourseProduct
from djangoapps.crm.models.erp_models import ClientOrder, Invoice
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
            document_number = ClientOrder.objects.count() + 1
            # todo: try match client
            client_order.number = f'CO-{document_number}'
            client_order.save()

            client_order.add_item(product, 1)

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
    return render(request, 'course_product.html', context)


def enrollment_accepted(request):
    return render(request, 'enrollment_accepted.html', {})


def invoice(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    context = {
        'invoice': invoice,
    }
    return render(request, 'invoice_payment.html', context)


def invoice_payment(request, uuid):
    invoice = Invoice.objects.get(uuid=uuid)
    payment_in = logic.create_yandex_payment_from_invoice(invoice)
    return redirect(payment_in.gateway_payment_url)

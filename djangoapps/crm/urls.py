from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path('order/product', views.order_single_product, name='order_single_product'),
    path('order/accepted', views.order_accepted, name='order_accepted'),
    path('invoice/<uuid:uuid>', views.invoice, name='invoice'),
    path('invoice/<uuid:uuid>/pay', views.invoice_payment, name='invoice_payment'),
    path('payment/<uuid:uuid>', views.payment_status, name='payment_status'),
]

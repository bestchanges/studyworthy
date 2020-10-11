from django.urls import path

from . import views

app_name = 'yandex_kassa'

urlpatterns = [
    path('invoice/<uuid:invoice_uuid>/pay', views.invoice_payment, name='invoice_payment'),
    path('payment/<uuid:payment_uuid>/status', views.update_payment_status, name='payment_status'),
]

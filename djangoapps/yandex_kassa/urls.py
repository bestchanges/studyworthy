from django.urls import path

from . import views

app_name = 'yandex_kassa'

urlpatterns = [
    path('invoice/<uuid:invoice_uuid>/pay', views.invoice_payment, name='invoice_payment'),
    path('invoice/<uuid:invoice_uuid>/update', views.update_payment_status, name='invoice_status'),
]

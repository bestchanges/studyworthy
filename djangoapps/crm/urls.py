from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path('course/<code>', views.course_product, name='course_product'),
    path('accepted-ok', views.enrollment_accepted, name='enrollment_accepted'),
    path('invoice/<uuid:uuid>', views.invoice, name='invoice'),
    path('invoice/<uuid:uuid>/pay', views.invoice_payment, name='invoice_payment'),
    path('payment/<uuid:uuid>', views.payment_status, name='payment_status'),
]

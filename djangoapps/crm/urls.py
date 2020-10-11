from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path('product/order', views.order_single_product, name='order_single_product'),
    path('order/<uuid:order_uuid>/accepted', views.order_accepted, name='order-accepted'),
    path('order/<uuid:order_uuid>/overview', views.order_overview, name='order-overview'),
    path('order/<uuid:order_uuid>/pay', views.order_pay, name='order-pay'),
    path('invoice/<uuid:uuid>', views.invoice, name='invoice'),
]

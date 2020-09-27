from django.contrib import admin

from djangoapps.crm.models.crm_models import CourseProduct
from djangoapps.crm.models.erp_models import ClientOrder, Invoice, PaymentIn, ClientOrderItem


class ClientOrderItemAdmin(admin.TabularInline):
    model = ClientOrderItem
    extra = 0


@admin.register(ClientOrder)
class ClientOrderAdmin(admin.ModelAdmin):
    inlines = [ClientOrderItemAdmin]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentIn)
class PaymentInAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseProduct)
class CourseProductAdmin(admin.ModelAdmin):
    pass

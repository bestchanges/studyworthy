from django.contrib import admin

from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import ClientOrder, ClientOrderItem, Invoice, PaymentIn, Person


class ClientOrderItemAdmin(admin.TabularInline):
    model = ClientOrderItem
    extra = 0


def fulfill(modeladmin, request, queryset):
    for client_order in queryset:
        client_order.fulfill()


@admin.register(ClientOrder)
class ClientOrderAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'document_date', 'client', 'state', 'amount', 'created_at']
    inlines = [ClientOrderItemAdmin]
    actions = [fulfill]


@admin.register(Person)
class PersonInvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentIn)
class PaymentInAdmin(admin.ModelAdmin):
    pass

@admin.register(CourseProduct)
class CourseProductAdmin(admin.ModelAdmin):
    pass

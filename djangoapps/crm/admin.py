from django.contrib import admin

from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Order, OrderItem, Invoice, Person, Payment


class ClientOrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0


def fulfill(modeladmin, request, queryset):
    for client_order in queryset:
        client_order.fulfill()


@admin.register(Order)
class ClientOrderAdmin(admin.ModelAdmin):
    list_display = ['document_number', 'document_date', 'buyer', 'state', 'amount', 'created_at']
    inlines = [ClientOrderItemAdmin]
    actions = [fulfill]


@admin.register(Person)
class PersonInvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentInAdmin(admin.ModelAdmin):
    pass


@admin.register(CourseProduct)
class CourseProductAdmin(admin.ModelAdmin):
    pass

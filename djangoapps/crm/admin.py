from django.contrib import admin

from djangoapps.crm.models.crm_models import CourseProduct
from djangoapps.crm.models.erp_models import ClientOrder, Invoice


@admin.register(ClientOrder)
class AdminClientOrder(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class AdminInvoice(admin.ModelAdmin):
    pass


@admin.register(CourseProduct)
class AdminCourseProduct(admin.ModelAdmin):
    pass

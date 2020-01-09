from django.contrib import admin

from crm.models.crm_models import CourseProduct, Enrollment


@admin.register(Enrollment)
class AdminCourseProduct(admin.ModelAdmin):
    pass


@admin.register(CourseProduct)
class AdminCourseProduct(admin.ModelAdmin):
    pass

from django.contrib import admin

from crm.models.crm_models import CourseProduct

@admin.register(CourseProduct)
class AdminCourseProduct(admin.ModelAdmin):
    pass

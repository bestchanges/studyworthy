from cms.extensions import PageExtension
from cms.models import CMSPlugin, Page
from django.db import models

from djangoapps.crm.models import CourseProduct
from djangoapps.lms.models.lms_models import Course


# Page extensions:

class CourseProductPageExtension(PageExtension):
    course_product = models.ForeignKey(CourseProduct, on_delete=models.PROTECT, related_name='page_extension')

    def __str__(self):
        return f'{self.course_product.name} ({self.get_page().get_path()})'

# CMS Plugins:

class CourseProductPageExtensionCMSPluginConfig(CMSPlugin):
    course_page_extension = models.ForeignKey(CourseProductPageExtension, on_delete=models.PROTECT)


class CourseProductCMSPluginConfig(CMSPlugin):
    course_product = models.ForeignKey(CourseProduct, on_delete=models.PROTECT)


class ManyCourseProductPageExtensionCMSPluginConfigg(CMSPlugin):
    course_page_extensions = models.ManyToManyField(CourseProductPageExtension, blank=True)

    def copy_relations(self, old_instance: 'ManyCourseProductPageExtensionCMSPluginConfigg'):
        for course_page_extension in old_instance.course_page_extensions.all():
            self.course_page_extensions.add(course_page_extension)
        super().copy_relations(old_instance)


class CourseCMSPluginConfig(CMSPlugin):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from djangoapps.crm.forms import SingleCourseProductOrderForm
from djangoapps.erp.models import Person
from djangoapps.siteroot.models import CourseProductCMSPluginConfig, CourseCMSPluginConfig, \
    CourseProductPageExtensionCMSPluginConfig, ManyCourseProductPageExtensionCMSPluginConfigg, \
    CourseProductPageExtension


@plugin_pool.register_plugin
class CourseCard(CMSPluginBase):

    model = CourseProductPageExtensionCMSPluginConfig
    name = _('Course Card')
    # TODO: make this cards: https://bootsnipp.com/snippets/92xNm
    render_template = "siteroot/cms_plugins/course_card.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance: CourseProductPageExtensionCMSPluginConfig, placeholder):
        context = super().render(context, instance, placeholder)
        context['course'] = instance.course_page_extension.course_product
        context['page'] = instance.course_page_extension.get_page()
        return context


@plugin_pool.register_plugin
class CoursesCatalogCard(CMSPluginBase):

    model = ManyCourseProductPageExtensionCMSPluginConfigg
    name = _('Course Catalog')
    render_template = "siteroot/cms_plugins/course_catalog.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance: ManyCourseProductPageExtensionCMSPluginConfigg, placeholder):
        context = super().render(context, instance, placeholder)

        course_page_extensions = instance.course_page_extensions
        if not course_page_extensions.count():
            course_page_extensions = CourseProductPageExtension.objects

        catalog = []
        for page_extension in course_page_extensions.all():
            catalog.append(
                {
                    'course': page_extension.course_product,
                    'page': page_extension.get_page()
                }
            )
        context['catalog'] = catalog
        return context


@plugin_pool.register_plugin
class CourseProductSignupCMSPlugin(CMSPluginBase):

    model = CourseProductCMSPluginConfig
    name = _('Course signup form')
    render_template = "siteroot/cms_plugins/course_signup.html"
    module = _(' LMS Control')
    cache = False


    def render(self, context, instance: CourseProductCMSPluginConfig, placeholder):

        course_product = instance.course_product
        context['course'] = course_product

        request = context['request']
        person = Person.objects.filter(user=request.user).first()
        form = SingleCourseProductOrderForm(product=course_product, person=person)
        context['form'] = form

        return context


@plugin_pool.register_plugin
class CourseProgramCMSPlugin(CMSPluginBase):

    model = CourseCMSPluginConfig
    name = _('Course program')
    render_template = "siteroot/cms_plugins/course_program.html"
    module = _(' LMS Control')
    cache = False

    def render(self, context, instance: CourseCMSPluginConfig, placeholder):
        context = super().render(context, instance, placeholder)
        context['course'] = instance.course
        return context

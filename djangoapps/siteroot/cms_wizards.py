import logging

from cms.api import add_plugin, create_page
from cms.cms_wizards import CMSPageWizard
from cms.models import Page
from cms.wizards.wizard_pool import wizard_pool
from django import forms
from django.utils.translation import (
    ugettext_lazy as _,
)

from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Product
from djangoapps.lms_cms.utils import get_placeholder
from djangoapps.siteroot.models import CourseProductPageExtension

logger = logging.getLogger(__name__)


class NewCourseForm(forms.Form):
    course_product = forms.ModelChoiceField(queryset=CourseProduct.objects.filter(state=Product.State.ACTIVE))

    def save(self, **kwargs):
        course_product: CourseProduct = self.cleaned_data['course_product']
        page = create_page(
            course_product.name,
            template='fullwidth.html',
            language='ru',
            published=True,
            in_navigation=True,
        )
        CourseProductPageExtension.objects.create(course_product=course_product, extended_object=page)

        # Let's create some default content
        content_placeholder = get_placeholder(page, slot='content')
        add_plugin(
            plugin_type='TextCMSPlugin',
            placeholder=content_placeholder, language=self.language_code,
            body=f'<h1>Курс: {course_product.name}</h1><p>{course_product.long_description}</p>'
        )
        add_plugin(
            plugin_type='CourseProgramCMSPlugin',
            placeholder=content_placeholder, language=self.language_code,
            course=course_product.course,
        )
        add_plugin(
            plugin_type='CourseProductSignupCMSPlugin',
            placeholder=content_placeholder, language=self.language_code,
            course_product=course_product,
        )

        return page


class NewCourseWizard(CMSPageWizard):
    pass


new_course_wizard = NewCourseWizard(
    title=_("Landing for Course Product"),
    description=_("Create landing page for existing course product"),
    weight=90,
    form=NewCourseForm,
    model=Page,
)
wizard_pool.register(new_course_wizard)

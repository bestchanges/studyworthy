from cms.models import Page
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse
from django.utils.translation import ugettext_lazy as _


def generate_admin_url(class_or_model):
    """If it's class then create link on admin form for create. If existing model then to update"""
    if class_or_model.pk:
        model = class_or_model
        return admin_reverse(
            f'{model._meta.app_label}_{model.__class__.__name__.lower()}_change',
            args=(model.pk,)
        )
    else:
        class_ = class_or_model
        return admin_reverse(
            f'{class_._meta.app_label}_{class_.__name__.lower()}_add',
        )


@toolbar_pool.register
class CourseToolbar(CMSToolbar):

    def populate(self):

        menu = self.toolbar.get_or_create_menu('lms-menu', 'LMS')
        if not menu:
            return
        
        # menu.add_modal_item(_('Course settings'), url=generate_admin_url(course))
        # menu.add_modal_item(_('Lesson settings'), url=generate_admin_url(lesson))

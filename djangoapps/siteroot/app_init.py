from cms.api import create_page, add_plugin
from cms.models import Page, Site
from cms.utils.permissions import current_user
from django.conf import settings
from django.contrib.auth.models import Group

from djangoapps.lms_cms import constants
from djangoapps.lms_cms.utils import get_placeholder


def create_home_page():
    page = create_page(
        title='Home',
        template=settings.CMS_TEMPLATES[0][0],
        language=settings.LANGUAGE_CODE,
    )
    placeholder = get_placeholder(page)
    plugin_data = {
        'body': f'<h1>Welcome to StudyWorthy</h1>'
    }
    add_plugin(placeholder=placeholder, plugin_type='TextPlugin', language=settings.LANGUAGE_CODE, **plugin_data)
    add_plugin(placeholder=placeholder, plugin_type='CoursesCatalogCard', language=settings.LANGUAGE_CODE)
    publish_page(page)


def publish_page(page: Page, by='admin'):
    with current_user(by):
        page.publish(settings.LANGUAGE_CODE)
    return page.reload()



def init():
    create_home_page()

import logging

from cms.api import create_page, add_plugin
from cms.models import Page
from cms.utils.permissions import current_user
from django.conf import settings
from django.urls import reverse

from djangoapps.lms_cms.utils import get_placeholder

logger = logging.getLogger(__name__)

def create_home_page():
    if Page.objects.filter(title_set__slug='home').first():
        logger.debug('Home page already exists')
        return
    page = create_page(
        title='Home',
        slug='home',
        template=settings.CMS_TEMPLATES[0][0],
        language=settings.LANGUAGE_CODE,
        published = True,
    )
    placeholder = get_placeholder(page)
    plugin_data = {
        'body': f'<h1>Welcome to StudyWorthy</h1>'
    }
    add_plugin(placeholder=placeholder, plugin_type='TextPlugin', language=settings.LANGUAGE_CODE, **plugin_data)
    add_plugin(placeholder=placeholder, plugin_type='CoursesCatalogCard', language=settings.LANGUAGE_CODE)
    publish_page(page)
    page.set_as_homepage()


def create_lms_page():
    """Create page which redirects to /lms/ app root"""
    if Page.objects.filter(title_set__slug='lms').first():
        logger.debug('LMS page already exists')
        return
    page = create_page(
        title='LMS',
        slug='lms',
        menu_title='Мои курсы',
        limit_visibility_in_menu=False,
        template=settings.CMS_TEMPLATES[0][0],
        language=settings.LANGUAGE_CODE,
        published = True,
        redirect=reverse('lms_cms:student_kabinet'),
    )
    publish_page(page)
    page.clear_cache(menu=True)


def publish_page(page: Page, by='admin'):
    with current_user(by):
        page.publish(settings.LANGUAGE_CODE)
    return page.reload()


def init():
    create_home_page()
    create_lms_page()

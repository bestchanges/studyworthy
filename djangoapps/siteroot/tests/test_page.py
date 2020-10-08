from cms.api import publish_page
from cms.models import Page
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from djangoapps.lms_cms.utils import create_home_page
from djangoapps.lms_cms.tests.utils import create_admin_user


class PageTestCase(TestCase):
    def setUp(self):
        # call_command('init')
        import djangoapps.lms_cms.app_init
        djangoapps.lms_cms.app_init.init()
        self.user_admin = create_admin_user()

    def test_create_home_page(self):
        page = create_home_page()
        publish_page(page, self.user_admin, language=settings.LANGUAGE_CODE)
        assert page.is_published(language=settings.LANGUAGE_CODE)
        page_id = page.id
        page.delete()
        assert not Page.objects.filter(id=page_id).exists()

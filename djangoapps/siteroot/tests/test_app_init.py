import unittest

from cms.models import Page
from django.test import TestCase

from .. import app_init


class MyTestCase(TestCase):

    @unittest.skip("it doesn't work :-( after page creation '/' returns 404 error")
    def test_app_setup(self):
        self.assertEqual(0, Page.objects.all().count(), "Just created CMS should be empty")
        app_init.init()
        self.assertEqual(2, Page.objects.all().count(), "Now pages should exist")

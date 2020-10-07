from django.test import TestCase

from djangoapps.crm import app_init
from djangoapps.crm.models import my_organization
from djangoapps.erp.models import Organization


class TestModels(TestCase):

    def test_init(self):
        self.assertRaises(Organization.DoesNotExist, my_organization)
        app_init.init()
        self.assertTrue(my_organization())

from django.contrib.auth.models import Group
from django.test import TestCase

from djangoapps.lms_cms.constants import TEACHERS_GROUP_NAME, STUDENTS_GROUP_NAME, ADMINS_GROUP_NAME


class MyTestCase(TestCase):

    def test_app_setup(self):
        """This groups should be created by migrations."""
        assert Group.objects.filter(name=TEACHERS_GROUP_NAME).exists()
        assert Group.objects.filter(name=STUDENTS_GROUP_NAME).exists()
        assert Group.objects.filter(name=ADMINS_GROUP_NAME).exists()


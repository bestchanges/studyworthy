from django.contrib.auth.models import Group
from django.test import TestCase

from djangoapps.lms_cms import app_init
from djangoapps.lms_cms.constants import TEACHERS_GROUP_NAME, STUDENTS_GROUP_NAME, ADMINS_GROUP_NAME


class MyTestCase(TestCase):

    def test_app_setup(self):
        for group_name in [TEACHERS_GROUP_NAME, STUDENTS_GROUP_NAME, ADMINS_GROUP_NAME]:
            assert not Group.objects.filter(name=group_name).exists()
        app_init.init()
        for group_name in [TEACHERS_GROUP_NAME, STUDENTS_GROUP_NAME, ADMINS_GROUP_NAME]:
            assert Group.objects.filter(name=group_name).exists()

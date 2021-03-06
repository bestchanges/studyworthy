from django.contrib.auth.models import Group

from djangoapps.lms_cms import constants


def create_groups():
    for group_name in constants.STUDENTS_GROUP_NAME, constants.TEACHERS_GROUP_NAME, constants.ADMINS_GROUP_NAME:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)


def init():
    print('LMS READY!')
    create_groups()

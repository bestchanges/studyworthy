from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site

from djangoapps.lms.models.lms_models import Student, Teacher, Admin
from djangoapps.lms_cms.constants import ADMINS_GROUP_NAME, TEACHERS_GROUP_NAME, STUDENTS_GROUP_NAME
from djangoapps.lms_cms.email import send_registration_email


def is_admin(user: User):
    return user.groups.filter(name=ADMINS_GROUP_NAME)


def is_teacher(user: User):
    return user.groups.filter(name=TEACHERS_GROUP_NAME)


def is_student(user: User):
    return user.groups.filter(name=STUDENTS_GROUP_NAME)


ROLE_TO_GROUPNAME_MAPPING = {
    Student.ROLE: STUDENTS_GROUP_NAME,
    Teacher.ROLE: TEACHERS_GROUP_NAME,
    Admin.ROLE: ADMINS_GROUP_NAME,
}


def create_lms_user(email, roles=(Student.ROLE,), password=None,
                    first_name='', last_name='',
                    send_email=True):
    if not password:
        password = User.objects.make_random_password()
    if not first_name:
        first_name = email.split('@')[0].capitalize()

    user = User(
        username=email,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    if Admin.ROLE in roles:
        user.is_superuser = True
        user.is_staff = True
    if Teacher.ROLE in roles:
        user.is_staff = True
    user.set_password(password)
    user.save()

    for role in roles:
        user.groups.add(Group.objects.get(name=ROLE_TO_GROUPNAME_MAPPING[role]))

    if send_email:
        send_registration_email(
            user=user,
            password=password
        )

    return user


def create_groups():
    """Create groups for Students, Teachers, Curators"""
    for group_name in STUDENTS_GROUP_NAME, TEACHERS_GROUP_NAME, ADMINS_GROUP_NAME:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)

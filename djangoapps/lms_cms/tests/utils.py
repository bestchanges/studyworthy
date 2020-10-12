import random
import string

from django.forms import BaseForm

from djangoapps.lms.models import Student, Admin
from djangoapps.lms_cms.logic.users import create_lms_user


def save_form(form: BaseForm):
    form.full_clean()
    return form.save()


def random_letters(size):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(size))


def create_teacher_user(email=None, password=None):
    if not email:
        email = f'teacher-{random_letters(4)}@localhost'
    return create_lms_user(email=email, roles=[Student.ROLE], password=password, send_email=False)


def create_admin_user(email=None, password=None):
    if not email:
        email = f'admin-{random_letters(4)}@localhost'
    return create_lms_user(email=email, roles=[Admin.ROLE], password=password, send_email=False)


def create_student_user(email=None, password=None):
    if not email:
        email = f'student-{random_letters(4)}@localhost'
    return create_lms_user(email=email, roles=[Student.ROLE], password=password, send_email=False)

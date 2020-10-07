import re
import unittest

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from djmoney.money import Money

from djangoapps.crm.forms import SingleCourseProductOrderForm
from djangoapps.crm.models import CourseProduct
from djangoapps.erp.models import Order
from djangoapps.lms.models.lms_models import Course


class SignupFormModelTestCase(TestCase):
    def setUp(self):
        call_command('init')
        self.course = Course.objects.create(title='test course')

    def test_order_form_required(self):
        product = CourseProduct.objects.create(
            code='test-prod',
            price=Money(0),
        )
        product.courses.add(self.course)

        form_data = {
            'product_code': product.code,
            'name': 'Some Student',
            'email': 'some@student.nea',
            'phone': '+28113',
        }
        form = SingleCourseProductOrderForm(
            data=form_data
        )
        self.assertTrue(form.is_valid(), form.errors)

        # test negative cases
        for required_field in 'product_code', 'name', 'email':
            form_data_copy = dict(form_data)
            del form_data_copy[required_field]
            form = SingleCourseProductOrderForm(
                data=form_data_copy
            )
            self.assertFalse(form.is_valid(), "Should raise errors")


    def test_enroll_new_student_on_free_course(self):
        """New (unknown) user fill the form for free course.

        The system should create User account.
        The system should send Email to his email with the password.
        Email + password should authenticate this user.
        Enrollment to course email notification should also be sent.
        """
        product = CourseProduct.objects.create(
            code='test-prod',
            price=Money(0),
        )
        product.courses.add(self.course)

        email = 'some@student.nea'
        name = 'Some Student'
        form_data = {
            'product_code': product.code,
            'name': name,
            'email': email,
            'phone': '+28113',
        }
        form = SingleCourseProductOrderForm(
            data=form_data
        )

        client_order = form.create_order()
        self.assertTrue(client_order.document_number)
        # buyer shall be created
        self.assertTrue(client_order.buyer.person)
        person = client_order.buyer.person
        self.assertEqual(email, person.email)
        self.assertEqual(name, person.full_name)
        self.assertEqual('Some', person.first_name)
        self.assertEqual('Student', person.last_name)

        # setting the state trigger signals for processing
        client_order.set_state(Order.State.NEW)
        # Free course shall be fulfilled on creation so let's check it
        self.assertEqual(Order.State.COMPLETED, client_order.state)

        # User shall be created. Signup email shall be sent.
        user = person.user
        self.assertTrue(user, "User shall be created")
        self.assertEqual('Some', user.first_name)
        self.assertEqual('Student', user.last_name)
        self.assertEqual(email, user.email)
        self.assertEqual(email, user.username)

        self.assertEqual(len(mail.outbox), 2)
        notification_email = mail.outbox[0]
        self.assertEqual(notification_email.to, [email])
        assert notification_email.body.find('example.com/accounts/login') > 0, "Should point to login page"
        # parse password from mail and try to login
        password = re.findall(r'пароль:\s*([^\s]+)', notification_email.body)[0]
        assert password
        auth_user = authenticate(username=email, password=password)  # type: User
        assert auth_user == user

    @unittest.skip("TODO")
    def test_enroll_for_existing_student(self):
        assert False

    @unittest.skip("TODO")
    def test_enroll_on_confirmation(self):
        assert False

    @unittest.skip("TODO")
    def test_enroll_on_partial_payment(self):
        assert False

    @unittest.skip("TODO")
    def test_enroll_on_full_payment(self):
        assert False

    @unittest.skip("TODO")
    def test_enroll_on_full_payment_when_fulfill_on_partial(self):
        "should also process"
        assert False

    @unittest.skip("TODO")
    def test_enroll_on_existing_group_flow(self):
        assert False


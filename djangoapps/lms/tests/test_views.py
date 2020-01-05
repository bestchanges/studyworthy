from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    fixtures = ['sample-persons.yaml', 'sample-course-hpi.yaml']

    def test_home_response(self):
        client = self.client  # type: Client
        with self.assertTemplateUsed('lms/index.html'):
            response = client.get(reverse('lms:index'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "index page")

    def test_courses_response(self):
        response = self.client.get(reverse('lms:courses'))
        self.assertEqual(response.status_code, 200)

    def test_course_response(self):
        response = self.client.get(reverse('lms:course', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_category_response(self):
        response = self.client.get(reverse('lms:category', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_lms_response(self):
        response = self.client.get(reverse('lms:study', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_lms_unit_response(self):
        response = self.client.get(reverse('lms:study_unit', kwargs={'pk': 1, 'unit_pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_user_response(self):
        response = self.client.get(reverse('lms:user'))
        self.assertEqual(response.status_code, 200)

    def test_user_lms_response(self):
        response = self.client.get(reverse('lms:user_lms_session'))
        self.assertEqual(response.status_code, 200)

    def test_user_settings_response(self):
        response = self.client.get(reverse('lms:user_settings'))
        self.assertEqual(response.status_code, 200)

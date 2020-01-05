from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    fixtures = ['sample-persons.yaml', 'sample-course-hpi.yaml']

    def test_home_response(self):
        client = self.client  # type: Client
        with self.assertTemplateUsed('campus/index.html'):
            response = client.get(reverse('campus:index'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "index page")

    def test_courses_response(self):
        response = self.client.get(reverse('campus:courses'))
        self.assertEqual(response.status_code, 200)

    def test_course_response(self):
        response = self.client.get(reverse('campus:course', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_lms_response(self):
        response = self.client.get(reverse('campus:study', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_lms_unit_response(self):
        response = self.client.get(reverse('campus:study_unit', kwargs={'pk': 1, 'unit_pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_user_response(self):
        response = self.client.get(reverse('campus:user'))
        self.assertEqual(response.status_code, 200)

    def test_user_settings_response(self):
        response = self.client.get(reverse('campus:user_settings'))
        self.assertEqual(response.status_code, 200)

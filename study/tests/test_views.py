from django.test import TestCase, Client
from django.urls import reverse


class ViewsTest(TestCase):
    fixtures = ['fixtures/sample-persons.yaml', 'fixtures/sample-course.yaml']

    def test_home_response(self):
        client = self.client  # type: Client
        with self.assertTemplateUsed('study/index.html'):
            response = client.get(reverse('study:index'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "index page")

    def test_courses_response(self):
        response = self.client.get(reverse('study:courses'))
        self.assertEqual(response.status_code, 200)

    def test_course_response(self):
        response = self.client.get(reverse('study:course', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_category_response(self):
        response = self.client.get(reverse('study:category', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_study_response(self):
        response = self.client.get(reverse('study:study', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_study_unit_response(self):
        response = self.client.get(reverse('study:study_unit', kwargs={'pk': 1, 'unit_pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_user_response(self):
        response = self.client.get(reverse('study:user'))
        self.assertEqual(response.status_code, 200)

    def test_user_study_response(self):
        response = self.client.get(reverse('study:user_study_session'))
        self.assertEqual(response.status_code, 200)

    def test_user_settings_response(self):
        response = self.client.get(reverse('study:user_settings'))
        self.assertEqual(response.status_code, 200)

from django.test import TestCase
from django.urls import reverse


class SimpleTest(TestCase):

    def test_courses_response(self):
        response = self.client.get(reverse('manage:courses'))
        self.assertEqual(response.status_code, 200)

    def test_course_start_response(self):
        response = self.client.get(reverse('manage:start_course', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_study_response(self):
        response = self.client.get(reverse('manage:study'))
        self.assertEqual(response.status_code, 200)

    def test_study_manage_response(self):
        response = self.client.get(reverse('manage:study_manage', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    fixtures = ['sample-admin.yaml', 'sample-persons.yaml', 'sample-course-hpi.yaml']

    def test_home_authenticated(self):
        client : Client = self.client
        assert client.login(username='admin', password='admin')
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "campus/index.html")

    def test_home_not_authenticated(self):
        client : Client = self.client
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 302)

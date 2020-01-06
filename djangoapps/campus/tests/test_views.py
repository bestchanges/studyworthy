from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    fixtures = ['sample-persons.yaml', 'sample-auth.yaml', 'sample-courses.yaml', 'sample-learnings.yaml']

    def test_home_authenticated(self):
        client : Client = self.client
        assert client.login(username='sample-student', password='User123!')
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "campus/index.html")

    def test_home_not_authenticated(self):
        client : Client = self.client
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 302)

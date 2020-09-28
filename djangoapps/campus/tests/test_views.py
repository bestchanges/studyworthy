from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='sample-student',
            email='email@sample-student.zzz',
            password='UserPassword'
        )

    def test_home_authenticated(self):
        client: Client = self.client
        assert client.login(username='sample-student', password='UserPassword')
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "campus/index.html")

    def test_home_not_authenticated(self):
        client: Client = self.client
        response = client.get(reverse('campus:index'))
        self.assertEqual(response.status_code, 302)

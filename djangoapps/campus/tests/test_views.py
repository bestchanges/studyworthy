from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from djangoapps.siteroot.models import SiteUser


class TestViews(TestCase):
    def setUp(self) -> None:
        self.user = SiteUser.objects.create_user(
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

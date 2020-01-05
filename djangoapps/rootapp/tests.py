from django.test import TestCase

# Create your tests here.
from django.urls import reverse


class TestViews(TestCase):

    def test_index(self):
        response = self.client.get(reverse('rootapp:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rootapp/index.html')

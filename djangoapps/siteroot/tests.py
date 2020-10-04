import unittest

from django.test import TestCase

# Create your tests here.
from django.urls import reverse


class TestViews(TestCase):

    @unittest.skip("Don't know how to test after application is attached to the CMS page")
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

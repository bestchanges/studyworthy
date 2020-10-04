from django.test import TestCase


class TestViews(TestCase):

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # TODO: (low) create pages structure on first start to avoid this
        self.assertTemplateUsed(response, 'cms/welcome.html')

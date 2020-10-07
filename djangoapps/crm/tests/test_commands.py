from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class CommandsTestCase(TestCase):
    def test_init(self):
        out = StringIO()
        call_command('init', stdout=out)
        self.assertIn('Init crm...', out.getvalue())
        self.assertIn('Init lms_cms...', out.getvalue())
        self.assertIn('Init done', out.getvalue())

    # TODO: test periodic
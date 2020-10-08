from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class CommandsTestCase(TestCase):
    def test_init(self):
        out = StringIO()
        call_command('init', stdout=out)
        self.assertIn('Init djangoapps.yandex_kassa...', out.getvalue())
        self.assertIn('Init done', out.getvalue())

    # TODO: test periodic
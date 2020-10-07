from importlib import import_module

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Initialize all applications. For every app the method app_init.init() will be called."

    def handle(self, *args, **options):
        for app in ['crm', 'lms_cms']:
            self.stdout.write(f"Init {app}...")
            module = import_module(f'djangoapps.{app}.app_init')
            module.init()
        self.stdout.write("Init done")

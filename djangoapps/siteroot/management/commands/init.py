from importlib import import_module

from django.apps import apps
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Initialize all applications. For every app the method app_init.init() will be called."

    def handle(self, *args, **options):
        for app_config in apps.get_app_configs():
            if hasattr(app_config, 'app_init'):
                self.stdout.write(f"Init {app_config.name}...")
                app_config.app_init()
        self.stdout.write("Init done")

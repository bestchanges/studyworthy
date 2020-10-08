from django.apps import apps
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Process periodic CRM tasks. Payments, etc."

    def handle(self, *args, **options):
        for app_config in apps.get_app_configs():
            if hasattr(app_config, 'periodic'):
                self.stdout.write(f"Periodic tasks for {app_config.name}...")
                app_config.periodic()
                self.stdout.write(f"Periodic tasks for {app_config.name} - DONE")
        self.stdout.write("Periodic done")

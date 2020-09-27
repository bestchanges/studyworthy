from django.core.management.base import BaseCommand, CommandError


# from djangoapps.crm.logic import
from djangoapps.crm import logic


class Command(BaseCommand):
    help = "Process periodic CRM tasks. Payments, etc."

    def handle(self, *args, **options):
        logic.run_periodic()
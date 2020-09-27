from django.core.management.base import BaseCommand

from djangoapps.crm.logic import payments


class Command(BaseCommand):
    help = "Process periodic CRM tasks. Payments, etc."

    def handle(self, *args, **options):
        payments.run_periodic()
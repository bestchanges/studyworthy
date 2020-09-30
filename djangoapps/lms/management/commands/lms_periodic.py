import logging

from django.core.management import BaseCommand

from djangoapps.lms.utils import lessons_open_ready, flows_start_ready


class Command(BaseCommand):
    help = 'Perform periodic tasks. It supposed to be run about 1 time per hour.'

    def handle(self, *args, **options):
        logging.info("Start flows ready to start... ")
        flows_start_ready()
        logging.info("Start flows ready to start: DONE")

        logging.info("Open lessons which are ready to be open... ")
        lessons_open_ready()
        logging.info("Open lessons which are ready to be open: DONE")

from django.apps import AppConfig

import logging

logger = logging.getLogger(__name__)

class LmsConfig(AppConfig):
    name = 'djangoapps.lms'
    verbose_name = 'LMS'

    def periodic(self):
        """
        Periodic tasks.
        Supposed to be run once peer hour.
        """

        from djangoapps.lms.utils import lessons_open_ready, flows_start_ready
        logger.info("Start flows ready to start... ")
        flows_start_ready()
        logger.info("Start flows ready to start: DONE")

        logger.info("Open lessons which are ready to be open... ")
        lessons_open_ready()
        logger.info("Open lessons which are ready to be open: DONE")

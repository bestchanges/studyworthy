from django.apps import AppConfig


class LmsConfig(AppConfig):
    name = 'djangoapps.lms'
    verbose_name = 'LMS'

    def ready(self):
        import djangoapps.lms.signal_handlers  # noqa

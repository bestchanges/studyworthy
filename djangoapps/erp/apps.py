from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'djangoapps.erp'

    def ready(self):
        from . import signal_handlers  # noqa:
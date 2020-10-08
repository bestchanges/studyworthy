from django.apps import AppConfig


class LmsCmsConfig(AppConfig):
    name = 'djangoapps.lms_cms'
    verbose_name = 'LMS CMS integration'

    def ready(self):
        import djangoapps.lms_cms.signal_handlers  # noqa

    def app_init(self):
        from . import app_init
        app_init.init()

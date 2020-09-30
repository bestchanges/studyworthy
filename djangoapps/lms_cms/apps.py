from django.apps import AppConfig


class LmsCmsConfig(AppConfig):
    name = 'djangoapps.lms_cms'
    verbose_name = 'LMS CMS integration'

    def ready(self):
        import djangoapps.lms_cms.signal_handlers  # noqa
        # from djangoapps.lms_cms.logic import users
        # users.create_groups()

from django.apps import AppConfig


class RootAppConfig(AppConfig):
    name = 'djangoapps.siteroot'

    def app_init(self):
        from . import app_init
        app_init.init()

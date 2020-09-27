from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'djangoapps.common'

    def ready(self):
        pass
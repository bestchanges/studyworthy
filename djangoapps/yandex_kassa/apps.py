from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'djangoapps.yandex_kassa'

    def ready(self):
        from . import api
        api.init()

    def app_init(self):
        from . import app_init
        app_init.init()

    def periodic(self):
        from . import logic
        logic.run_periodic()
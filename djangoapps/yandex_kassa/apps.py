from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'djangoapps.yandex_kassa'

    def ready(self):
        from . import api
        api.init()
        from djangoapps.crm.logic import payments
        from . import logic
        payments.register_gateway(logic.YandexKassa)

    def app_init(self):
        from . import app_init
        app_init.init()

    def periodic(self):
        from . import periodic
        periodic.periodic()
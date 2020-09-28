from django.apps import AppConfig

from djangoapps.crm.api import yandex_kassa


class MyAppConfig(AppConfig):
    name = 'djangoapps.crm'

    def ready(self):
        yandex_kassa.init()

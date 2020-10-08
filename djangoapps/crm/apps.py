from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'djangoapps.crm'

    def ready(self):
        import djangoapps.crm.signal_handlers  # noqa

    def app_init(self):
        """
        Application one-time initialization.
        Usually triggered by management command init

        Should be run on first application launch after configuration done.
        It's safe to run multiple times.
        """
        from . import app_init
        app_init.init()

    def register_payment_app(self, payment_app_config: AppConfig, invoice_payment_viewname=None, invoice_status_update_viewname=None):
        from . import config
        code = payment_app_config.label
        config.payments_apps[code] = {
            'payment_name': payment_app_config.verbose_name,
            'payment_code': code,
            'invoice_payment_viewname': invoice_payment_viewname,
            'invoice_status_update_viewname': invoice_status_update_viewname,
        }
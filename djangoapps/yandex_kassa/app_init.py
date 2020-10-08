from djangoapps.erp.models import Organization
from . import config


def create_organization():
    code = config.ORGANIZATION_CODE
    if not Organization.objects.filter(code=code).first():
        Organization.objects.create(
            code=code,
            name=config.ORGANIZATION_NAME,
        )


def register_payment_provider():
    import djangoapps.crm.config
    djangoapps.crm.config.PAYMENTS_PROVIDERS[config.PAYMENT_PROVIDER_CODE] = \
        (config.PAYMENT_PROVIDER_NAME, 'yandex_kassa:pay_invoice')


def init():
    create_organization()
    register_payment_provider()
from django.conf import settings

from djangoapps.erp.models import Organization


def create_organization():
    code = settings.MY_ORGANIZATION_CODE
    if not Organization.objects.filter(code=code).first():
        Organization.objects.create(
            code=code,
            name=settings.MY_ORGANIZATION_NAME,
        )


def init():
    create_organization()
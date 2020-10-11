from cms.utils.urlutils import urljoin
from django.conf import settings
from django.contrib.sites.models import Site


def build_full_url(path, site=None):
    if not site:
        site = Site.objects.get_current()
    full_url = "{protocol}://{domain}{path}".format(
        protocol=settings.HTTP_PROTOCOL,
        domain=site.domain,
        path=path,
    )
    return full_url

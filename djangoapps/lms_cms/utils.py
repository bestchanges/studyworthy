from cms.api import create_page, add_plugin
from cms.models import Page
from django.conf import settings


def get_placeholder(page, slot=None):
    """
    Returns the named placeholder or, if no «slot» provided, the first
    editable, non-static placeholder or None.
    """
    placeholders = page.get_placeholders()

    if slot:
        placeholders = placeholders.filter(slot=slot)

    for ph in placeholders:
        if not ph.is_static and ph.is_editable:
            return ph

    return None


def create_home_page() -> Page:
    page = create_page(
        title='Home',
        slug='home',
        template=settings.CMS_TEMPLATES[0][0],
        language=settings.LANGUAGE_CODE,
    )
    placeholder = get_placeholder(page)
    plugin_data = {
        'body': 'sample body'
    }
    add_plugin(placeholder=placeholder, plugin_type='TextPlugin', language=settings.LANGUAGE_CODE, **plugin_data)
    return page



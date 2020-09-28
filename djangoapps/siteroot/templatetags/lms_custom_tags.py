import markdown
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from djangoapps.erp.models import Person
from djangoapps.lms.models.content import Content

register = template.Library()


@register.filter(name='markdown')
def as_markdown(value):
    content = markdown.markdown(value)
    return mark_safe(content)


@register.simple_tag()
def person_avatar(person: Person):
    if person and hasattr(person, 'avatar_url') and person.avatar_url:
        image_url = person.avatar_url
    else:
        image_url = static('default-avatar.png')
    content = f'<img src="{image_url}" width=50 height=50 alt="" class="rounded-circle">'
    return mark_safe(content)


@register.simple_tag()
def render_content(content_object: Content):
    content_type = content_object.type
    if content_type == content_object.ContentType.MARKDOWN:
        content = markdown.markdown(content_object.text)
    else:
        content = f"Unknown content-type {content_type} for Content # {content_object.id}"
    return mark_safe(content)
